from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .logger_setup import setup_logger
from .read_dicom import find_dicom_files, read_study_metadata
from .group_series import group_dicoms_by_series_uid
from .validate_slices import validate_slice_counts

from .metrics.uniformity import calculate_piu_for_series
from .metrics.snr import calculate_snr


LOGGER = setup_logger()


def load_tolerances(tolerances_path: str | None) -> dict[str, Any]:
    """
    Load tolerances from config JSON, or return defaults if not provided.
    """
    defaults = {
        "slice_counts": {
            "3-Plane Localizer": 3,
            "SAG T1 SE": 11,
        },
        "piu_threshold": 80,
        "snr_threshold": 50,
    }

    if not tolerances_path:
        return defaults

    path = Path(tolerances_path)
    if not path.exists():
        return defaults

    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # merge defaults with cfg (cfg overrides)
    merged = defaults.copy()
    merged.update(cfg)
    merged["slice_counts"] = {**defaults.get("slice_counts", {}), **cfg.get("slice_counts", {})}
    return merged


def run_pipeline(data_folder: str, tolerances_path: str | None, report_path: str) -> dict[str, Any]:
    LOGGER.info("Starting ACR QA Pipeline")

    dicom_files = find_dicom_files(data_folder)
    if not dicom_files:
        raise FileNotFoundError(f"No DICOM files found in: {data_folder}")

    tolerances = load_tolerances(tolerances_path)

    study_meta = read_study_metadata(dicom_files[0])
    series_list = group_dicoms_by_series_uid(dicom_files)

    # Slice validation
    expected_slice_counts = tolerances.get("slice_counts", {})
    slice_validation = validate_slice_counts(series_list, expected_slice_counts)

    # Metrics
    metrics_results: list[dict[str, Any]] = []

    piu_threshold = float(tolerances.get("piu_threshold", 80))
    snr_threshold = float(tolerances.get("snr_threshold", 50))

    for series in series_list:
        desc = series.get("SeriesDescription", "")
        # Only calculate PIU for T1 series (example rule)
        if "T1" in desc:
            metrics_results.append(calculate_piu_for_series(series, piu_threshold=piu_threshold))

        # SNR placeholder (optional later)
        # metrics_results.append(calculate_snr(series, snr_threshold=snr_threshold))

    report = {
        "report_generated": datetime.now().isoformat(),
        "dataset": Path(data_folder).name,
        "data_folder": str(data_folder),
        "study_metadata": study_meta,
        "series": [
            {
                "SeriesInstanceUID": s["SeriesInstanceUID"],
                "SeriesDescription": s["SeriesDescription"],
                "slice_count": s["slice_count"],
                "instance_range": list(s["instance_range"]),
            }
            for s in series_list
        ],
        "qa_results": {
            "slice_count_validation": slice_validation,
            "metrics": metrics_results,
        },
    }

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    LOGGER.info("Report generated successfully")
    return report


def main():
    parser = argparse.ArgumentParser(description="ACR QA Pipeline")
    parser.add_argument("--data", required=True, help="Path to dataset folder (example: data\\ballinasloe)")
    parser.add_argument("--tolerances", required=False, default=None, help="Path to tolerances JSON (optional)")
    parser.add_argument("--out", required=False, default=None, help="Output report path (optional)")
    args = parser.parse_args()

    data_folder = args.data
    out_path = args.out

    if not out_path:
        dataset_name = Path(data_folder).name
        out_path = str(Path("reports") / f"report_{dataset_name}.json")

    report = run_pipeline(data_folder=data_folder, tolerances_path=args.tolerances, report_path=out_path)

    print(f"\n✅ Report created: {out_path}\n")
    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()