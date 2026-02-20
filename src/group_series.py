from __future__ import annotations

from collections import defaultdict
from typing import Any

import pydicom


def group_dicoms_by_series_uid(dicom_files: list[str]) -> list[dict[str, Any]]:
    """
    Groups DICOM files by SeriesInstanceUID.
    Returns a list of series dictionaries.
    """
    series_map: dict[str, dict[str, Any]] = defaultdict(lambda: {"files": [], "SeriesDescription": "N/A"})

    for f in dicom_files:
        try:
            ds = pydicom.dcmread(f, stop_before_pixels=True)
        except Exception:
            continue

        uid = getattr(ds, "SeriesInstanceUID", None)
        if not uid:
            continue

        series_map[uid]["SeriesInstanceUID"] = uid
        series_map[uid]["SeriesDescription"] = getattr(ds, "SeriesDescription", "N/A")
        series_map[uid]["files"].append(f)

    series_list: list[dict[str, Any]] = []

    def inst_num(path: str) -> int:
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            return int(getattr(ds, "InstanceNumber", 0) or 0)
        except Exception:
            return 0

    for uid, info in series_map.items():
        files_sorted = sorted(info["files"], key=inst_num)
        instance_numbers = [inst_num(p) for p in files_sorted]
        if instance_numbers:
            min_inst, max_inst = min(instance_numbers), max(instance_numbers)
        else:
            min_inst, max_inst = 0, 0

        series_list.append(
            {
                "SeriesInstanceUID": uid,
                "SeriesDescription": info.get("SeriesDescription", "N/A"),
                "files": files_sorted,
                "slice_count": len(files_sorted),
                "instance_range": (min_inst, max_inst),
            }
        )

    return series_list