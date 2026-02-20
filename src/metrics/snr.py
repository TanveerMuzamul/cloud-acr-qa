from __future__ import annotations
from typing import Any


def calculate_snr(series: dict[str, Any], snr_threshold: float = 50.0) -> dict[str, Any]:
    """
    Placeholder SNR metric (for now).
    You can implement later.
    """
    return {
        "SeriesDescription": series.get("SeriesDescription", "N/A"),
        "SeriesInstanceUID": series.get("SeriesInstanceUID", "N/A"),
        "SNR": None,
        "status": "NOT_IMPLEMENTED",
    }