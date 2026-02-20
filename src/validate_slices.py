from __future__ import annotations
from typing import Any


def validate_slice_counts(series_list: list[dict[str, Any]], expected_slice_counts: dict[str, int]) -> list[dict[str, Any]]:
    """
    Validate slice count per series by SeriesDescription.
    expected_slice_counts example:
      {"3-Plane Localizer": 3, "SAG T1 SE": 11}
    """
    results: list[dict[str, Any]] = []

    for s in series_list:
        desc = s.get("SeriesDescription", "N/A")
        uid = s.get("SeriesInstanceUID", "N/A")
        actual = int(s.get("slice_count", 0))
        expected = expected_slice_counts.get(desc)

        if expected is None:
            status = "NO_RULE"
        else:
            status = "PASS" if actual == int(expected) else "FAIL"

        results.append(
            {
                "SeriesDescription": desc,
                "SeriesInstanceUID": uid,
                "actual": actual,
                "expected": expected,
                "status": status,
            }
        )

    return results