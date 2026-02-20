from __future__ import annotations

from typing import Any

import numpy as np
import pydicom


def _to_float_pixels(ds) -> np.ndarray:
    arr = ds.pixel_array.astype(np.float32)
    # Apply rescale if present
    slope = float(getattr(ds, "RescaleSlope", 1.0) or 1.0)
    intercept = float(getattr(ds, "RescaleIntercept", 0.0) or 0.0)
    return arr * slope + intercept


def calculate_piu_for_series(series: dict[str, Any], piu_threshold: float = 80.0) -> dict[str, Any]:
    """
    Calculate Percent Integral Uniformity (PIU) for a series.
    Simple approach:
      - take middle slice
      - use central ROI (50% width/height)
      - PIU = (1 - (max-min)/(max+min)) * 100
    """
    files = series.get("files", [])
    if not files:
        return {
            "SeriesDescription": series.get("SeriesDescription", "N/A"),
            "SeriesInstanceUID": series.get("SeriesInstanceUID", "N/A"),
            "PIU": None,
            "status": "SKIP_NO_FILES",
        }

    mid_index = len(files) // 2
    ds = pydicom.dcmread(files[mid_index])  # need pixels
    img = _to_float_pixels(ds)

    h, w = img.shape
    y1, y2 = int(h * 0.25), int(h * 0.75)
    x1, x2 = int(w * 0.25), int(w * 0.75)
    roi = img[y1:y2, x1:x2]

    maxv = float(np.max(roi))
    minv = float(np.min(roi))

    if maxv + minv == 0:
        piu = 0.0
    else:
        piu = (1.0 - ((maxv - minv) / (maxv + minv))) * 100.0

    status = "PASS" if piu >= float(piu_threshold) else "FAIL"

    return {
        "SeriesDescription": series.get("SeriesDescription", "N/A"),
        "SeriesInstanceUID": series.get("SeriesInstanceUID", "N/A"),
        "PIU": round(float(piu), 2),
        "status": status,
    }