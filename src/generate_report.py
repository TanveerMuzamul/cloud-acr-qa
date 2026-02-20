import os
import json
import pydicom
from collections import defaultdict
from datetime import datetime

DICOM_FOLDER = "../data/ballinasloe"
REPORT_FOLDER = "../reports"

def find_dicom_files(folder_path):
    dicom_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    return dicom_files

def get_study_metadata(sample_file):
    ds = pydicom.dcmread(sample_file, stop_before_pixels=True)

    return {
        "StudyDate": getattr(ds, "StudyDate", "N/A"),
        "StudyDescription": getattr(ds, "StudyDescription", "N/A"),
        "Manufacturer": getattr(ds, "Manufacturer", "N/A"),
        "ModelName": getattr(ds, "ManufacturerModelName", "N/A"),
        "MagneticFieldStrength": getattr(ds, "MagneticFieldStrength", "N/A"),
    }

def count_slices_by_series(dicom_files):
    counts = defaultdict(int)

    for file in dicom_files:
        ds = pydicom.dcmread(file, stop_before_pixels=True)
        desc = getattr(ds, "SeriesDescription", "NoDescription")
        counts[desc] += 1

    return dict(counts)

def generate_report():
    files = find_dicom_files(DICOM_FOLDER)

    if len(files) == 0:
        raise Exception("No DICOM files found. Check DICOM_FOLDER path.")

    metadata = get_study_metadata(files[0])
    slice_counts = count_slices_by_series(files)

    report = {
        "report_generated": datetime.now().isoformat(),
        "dataset": "ballinasloe",
        "study_metadata": metadata,
        "series_slice_counts": slice_counts,
        "qa_results": {
            "slice_count_check": "PARTIAL (rules not applied yet)",
            "metrics": []
        }
    }

    os.makedirs(REPORT_FOLDER, exist_ok=True)

    report_path = os.path.join(REPORT_FOLDER, "report_ballinasloe.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    print(f"✅ Report created: {report_path}")

if __name__ == "__main__":
    generate_report()