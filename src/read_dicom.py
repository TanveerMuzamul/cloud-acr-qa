from __future__ import annotations

from pathlib import Path
from typing import Any

import pydicom


def find_dicom_files(data_folder: str) -> list[str]:
    """
    Find all DICOM files under the given data_folder.
    We consider .dcm files + also include files with no extension that are DICOM.
    """
    root = Path(data_folder)
    if not root.exists():
        return []

    dicom_files: list[str] = []

    # Common: .dcm
    dicom_files.extend([str(p) for p in root.rglob("*.dcm")])

    # Some datasets have DICOM with no extension; try to detect a few
    for p in root.rglob("*"):
        if p.is_file() and p.suffix == "" and p.name.upper() != "DICOMDIR":
            try:
                pydicom.dcmread(str(p), stop_before_pixels=True)
                dicom_files.append(str(p))
            except Exception:
                pass

    return sorted(list(set(dicom_files)))


def read_study_metadata(first_dicom_file: str) -> dict[str, Any]:
    """
    Read basic metadata from the first DICOM file.
    """
    ds = pydicom.dcmread(first_dicom_file, stop_before_pixels=True)

    def safe_get(name: str, default="N/A"):
        return getattr(ds, name, default)

    meta = {
        "StudyDate": safe_get("StudyDate"),
        "StudyDescription": safe_get("StudyDescription"),
        "Manufacturer": safe_get("Manufacturer"),
        "ModelName": safe_get("ManufacturerModelName", safe_get("ModelName")),
        "MagneticFieldStrength": safe_get("MagneticFieldStrength", None),
    }
    return meta