import argparse
import json
import os
from datetime import datetime

from .logger_setup import setup_logger
from .read_dicom import find_dicom_files, load_dicom_headers
from .group_series import group_dicoms_by_series, summarize_series
from .validate_slices import validate_slice_counts
from .generate_report import extract_study_metadata, save_report


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

    # collect all files under data folder
    all_files = find_dicom_files(data_folder)

    # read dicom headers only
    datasets = load_dicom_headers(all_files)

    if not datasets:
        logger.error("No DICOM files found. Check the data folder path.")
        raise SystemExit(1)

    # group by SeriesInstanceUID
    grouped = group_dicoms_by_series(datasets)

    # summarize series
    series_summaries = summarize_series(grouped)

    # load tolerance rules
    tolerances = load_tolerances(tolerances_path)

    # validate slice counts
    slice_validation = validate_slice_counts(series_summaries, tolerances)

    # report JSON
    dataset = dataset_name_from_path(data_folder)
    report = {
        "report_generated": datetime.now().isoformat(),
        "dataset": dataset,
        "data_folder": data_folder,
        "study_metadata": extract_study_metadata(datasets),
        "series": series_summaries,
        "qa_results": {
            "slice_count_validation": slice_validation,
            "metrics": []
        }
    }

    save_report(report, report_path)
    logger.info("Report generated successfully")

    print(f"\n✅ Report created: {report_path}\n")
    print("Pipeline finished successfully.")


def main():
    parser = argparse.ArgumentParser(description="ACR MRI QA pipeline (basic)")
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
        help="Output report path (default: reports/report_<dataset>.json)"
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