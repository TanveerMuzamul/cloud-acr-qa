import os
import pydicom
from collections import defaultdict

DICOM_FOLDER = "../data/ballinasloe"

# For now only validating localizer count (from your dataset)
EXPECTED_COUNTS_BY_DESCRIPTION = {
    "3-Plane Localizer": 3
}

def find_dicom_files(folder_path):
    dicom_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    return dicom_files

def count_by_series_uid(dicom_files):
    series = defaultdict(lambda: {"desc": "NoDescription", "count": 0})

    for file in dicom_files:
        ds = pydicom.dcmread(file, stop_before_pixels=True)
        uid = getattr(ds, "SeriesInstanceUID", "UNKNOWN_SERIES")
        desc = getattr(ds, "SeriesDescription", "NoDescription")

        series[uid]["desc"] = desc
        series[uid]["count"] += 1

    return series

if __name__ == "__main__":
    files = find_dicom_files(DICOM_FOLDER)
    series = count_by_series_uid(files)

    print("\nSlice count validation (per SeriesInstanceUID):\n")

    for uid, info in series.items():
        desc = info["desc"]
        count = info["count"]

        if desc in EXPECTED_COUNTS_BY_DESCRIPTION:
            expected = EXPECTED_COUNTS_BY_DESCRIPTION[desc]
            status = "PASS" if count == expected else "FAIL"
            print(f"{desc} | UID={uid[-8:]} | slices={count} (expected {expected}) → {status}")
        else:
            print(f"{desc} | UID={uid[-8:]} | slices={count} (no expected value set yet)")