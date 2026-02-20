import os
import pydicom

# Path to your DICOM data
DICOM_FOLDER = "../data/ballinasloe"

def load_dicom_files(folder_path):
    dicom_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))

    return dicom_files


if __name__ == "__main__":
    files = load_dicom_files(DICOM_FOLDER)

    print(f"\nFound {len(files)} DICOM files\n")

    for file in files[:5]:  # show only first 5 files
        ds = pydicom.dcmread(file)
        print("File:", file)
        print("Series Description:", getattr(ds, "SeriesDescription", "N/A"))
        print("Instance Number:", getattr(ds, "InstanceNumber", "N/A"))
        print("Rows:", getattr(ds, "Rows", "N/A"))
        print("Columns:", getattr(ds, "Columns", "N/A"))
        print("-" * 40)