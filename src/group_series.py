import os
import pydicom
from collections import defaultdict

DICOM_FOLDER = "../data/ballinasloe"

def find_dicom_files(folder_path):
    dicom_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    return dicom_files

def group_by_series(dicom_files):
    series_map = defaultdict(list)

    for file in dicom_files:
        ds = pydicom.dcmread(file, stop_before_pixels=True)
        series_uid = getattr(ds, "SeriesInstanceUID", "UNKNOWN_SERIES")
        series_desc = getattr(ds, "SeriesDescription", "NoDescription")

        series_map[series_uid].append({
            "file": file,
            "desc": series_desc,
            "instance": getattr(ds, "InstanceNumber", 0)
        })

    # sort each series by InstanceNumber
    for uid in series_map:
        series_map[uid] = sorted(series_map[uid], key=lambda x: x["instance"])

    return series_map

if __name__ == "__main__":
    files = find_dicom_files(DICOM_FOLDER)
    print(f"Found {len(files)} DICOM files\n")

    series_map = group_by_series(files)

    print(f"Found {len(series_map)} series:\n")

    for uid, items in series_map.items():
        desc = items[0]["desc"]
        count = len(items)
        first_inst = items[0]["instance"]
        last_inst = items[-1]["instance"]
        print(f"- {desc} | slices={count} | instance range={first_inst}..{last_inst}")