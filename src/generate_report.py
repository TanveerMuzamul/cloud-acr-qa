import json
import os
from datetime import datetime
from typing import Dict, List

def extract_study_metadata(datasets) -> Dict:
    # use first dicom as reference
    if not datasets:
        return {}

    ds = datasets[0][1]
    return {
        "StudyDate": getattr(ds, "StudyDate", "N/A"),
        "StudyDescription": getattr(ds, "StudyDescription", "N/A"),
        "Manufacturer": getattr(ds, "Manufacturer", "N/A"),
        "ModelName": getattr(ds, "ManufacturerModelName", getattr(ds, "ModelName", "N/A")),
        "MagneticFieldStrength": getattr(ds, "MagneticFieldStrength", "N/A"),
    }

def save_report(report: Dict, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)