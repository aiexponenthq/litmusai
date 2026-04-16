"""Override management — FR-10, US-17."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from litmusai.models.report import OverrideEntry, ScreeningReport


def load_overrides(path: Path) -> list[OverrideEntry]:
    """Load override entries from a JSON file."""
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        msg = f"Override file must contain a JSON array, got {type(data).__name__}"
        raise ValueError(msg)
    return [OverrideEntry.model_validate(item) for item in data]


def apply_overrides(report: ScreeningReport, overrides: list[OverrideEntry]) -> ScreeningReport:
    """Apply human overrides to a screening report, returning a new report."""
    data = report.model_dump()

    applied: list[dict[str, Any]] = []
    for override in overrides:
        cat_id = override.category
        if cat_id not in data["categories"]:
            continue
        cat = data["categories"][cat_id]
        if cat["verdict"] != override.verdict_before:
            continue
        cat["verdict"] = override.verdict_after
        applied.append(override.model_dump())

    data["overrides_applied"] = applied

    all_verdicts = [c["verdict"] for c in data["categories"].values()]
    data["summary"]["overall_verdict"] = (
        "red" if "red" in all_verdicts else "amber" if "amber" in all_verdicts else "clear"
    )
    data["summary"]["red_count"] = all_verdicts.count("red")
    data["summary"]["amber_count"] = all_verdicts.count("amber")
    data["summary"]["clear_count"] = all_verdicts.count("clear")
    data["summary"]["requires_legal_review"] = data["summary"]["overall_verdict"] in (
        "red",
        "amber",
    )

    return ScreeningReport.model_validate(data)
