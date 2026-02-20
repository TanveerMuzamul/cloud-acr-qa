import argparse
import json
import os
from datetime import datetime

import pydicom

from .logger_setup import setup_logger
from .read_dicom import find_dicom_files, load_dicom_headers
from .group_series import group_dicoms_by_series, summarize_series
from .validate_slices import validate_slice_counts
from .generate_report import extract_study_metadata, save_report
from .metrics.uniformity import calculate_piu


def load_tolerances(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dataset_name_from_path(path: str) -> str:
    return os.path.basename(os.path.normpath(path))


def run_pipeline(data_folder: str, tolerances_path: str, report_path: str):
    logger = setup_logger("logs/pipeline.log")
    logger.info("Starting ACR QA Pipeline")

    # Find all files
    all_files = find_dicom_files(data_folder)

    # Load DICOM headers only
    datasets = load_dicom_headers(all_files)

    if not datasets:
        logger.error("No DICOM files found. Check the data folder path.")
        raise SystemExit(1)

    # Group by series
    grouped = group_dicoms_by_series(datasets)

    # Create series summary
    series_summaries = summarize_series(grouped)

    # Load tolerance rules
    tolerances = load_tolerances(tolerances_path)

    # Validate slice counts
    slice_validation = validate_slice_counts(series_summaries, tolerances)

    # --------------------------------
    # Uniformity (PIU) calculation
    # --------------------------------
    uniformity_results = []

    for uid, items in grouped.items():
        ds0 = items[0][1]
        desc = getattr(ds0, "SeriesDescription", "N/A")

        # Only calculate for T1 series
        if "T1" in desc:
            middle_index = len(items) // 2
            middle_path = items[middle_index][0]

            try:
                # Read full DICOM (including pixel data)
                ds_full = pydicom.dcmread(middle_path)
                pixel_array = ds_full.pixel_array

                piu_value = calculate_piu(pixel_array)

                uniformity_results.append({
                    "SeriesDescription": desc,
                    "SeriesInstanceUID": uid,
                    "PIU": piu_value,
                    "status": "PASS" if piu_value >= 80 else "FAIL"
                })

            except Exception as e:
                print("Uniformity calculation failed:", e)
                continue

    # Build report
    dataset = dataset_name_from_path(data_folder)

    report = {
        "report_generated": datetime.now().isoformat(),
        "dataset": dataset,
        "data_folder": data_folder,
        "study_metadata": extract_study_metadata(datasets),
        "series": series_summaries,
        "qa_results": {
            "slice_count_validation": slice_validation,
            "metrics": uniformity_results
        }
    }

    save_report(report, report_path)
    logger.info("Report generated successfully")

    print(f"\n✅ Report created: {report_path}\n")
    print("Pipeline finished successfully.")


def main():
    parser = argparse.ArgumentParser(description="ACR MRI QA pipeline")
    parser.add_argument(
        "--data",
        required=True,
        help="Path to dataset folder (example: data\\ballinasloe)"
    )
    parser.add_argument(
        "--tolerances",
        default="config/tolerances.json",
        help="Tolerances JSON path"
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output report path"
    )

    args = parser.parse_args()

    data_folder = args.data
    dataset = dataset_name_from_path(data_folder)

    out_path = args.out.strip()
    if not out_path:
        out_path = f"reports/report_{dataset}.json"

    run_pipeline(
        data_folder=data_folder,
        tolerances_path=args.tolerances,
        report_path=out_path
    )


if __name__ == "__main__":
    main()