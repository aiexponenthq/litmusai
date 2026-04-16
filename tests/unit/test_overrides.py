"""Unit tests for the overrides engine — FR-10, US-17."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

import pytest

from litmusai.engine.overrides import apply_overrides
from litmusai.engine.screener import Screener
from litmusai.models.report import OverrideEntry, ScreeningReport
from litmusai.models.ruleset import Ruleset
from litmusai.models.system import SystemDescription

RULESET_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "src"
    / "litmusai"
    / "_data"
    / "ruleset"
    / "ruleset-2024-1689-v0.1.json"
)


@pytest.fixture
def ruleset() -> Ruleset:
    return Ruleset.model_validate(json.loads(RULESET_PATH.read_text()))


@pytest.fixture
def screener(ruleset: Ruleset) -> Screener:
    return Screener(ruleset)


@pytest.fixture
def amber_report(screener: Screener, minimal_system_dict: dict[str, Any]) -> ScreeningReport:
    d = deepcopy(minimal_system_dict)
    d["outputs"]["emotion_inferences"] = True
    d["deployment_context"]["healthcare"] = True
    d["purpose"] = "Pain assessment"
    d["system_description"] = "Medical emotion inference"
    system = SystemDescription(**d)
    return screener.screen(system, timestamp=datetime(2026, 4, 16, tzinfo=UTC))


class TestApplyOverrides:
    def test_override_amber_to_clear(self, amber_report: ScreeningReport) -> None:
        assert amber_report.categories["5.1.f"].verdict == "amber"
        override = OverrideEntry(
            category="5.1.f",
            verdict_before="amber",
            verdict_after="clear",
            rationale="Legal confirmed healthcare exception applies.",
            approver="Jane Counsel",
            approver_email="jane@example.org",
            approved_at=datetime(2026, 4, 16, tzinfo=UTC),
        )
        result = apply_overrides(amber_report, [override])
        assert result.categories["5.1.f"].verdict == "clear"
        assert len(result.overrides_applied) == 1
        assert result.overrides_applied[0].approver == "Jane Counsel"

    def test_override_recalculates_summary(self, amber_report: ScreeningReport) -> None:
        override = OverrideEntry(
            category="5.1.f",
            verdict_before="amber",
            verdict_after="clear",
            rationale="Legal sign-off.",
            approver="Counsel",
            approver_email="c@example.org",
            approved_at=datetime(2026, 4, 16, tzinfo=UTC),
        )
        result = apply_overrides(amber_report, [override])
        assert result.summary.overall_verdict == "clear"
        assert result.summary.amber_count == 0
        assert result.summary.clear_count == 8

    def test_override_wrong_verdict_before_is_skipped(self, amber_report: ScreeningReport) -> None:
        override = OverrideEntry(
            category="5.1.f",
            verdict_before="red",
            verdict_after="clear",
            rationale="Mismatch — should be skipped.",
            approver="X",
            approver_email="x@example.org",
            approved_at=datetime(2026, 4, 16, tzinfo=UTC),
        )
        result = apply_overrides(amber_report, [override])
        assert result.categories["5.1.f"].verdict == "amber"
        assert len(result.overrides_applied) == 0

    def test_override_nonexistent_category_skipped(self, amber_report: ScreeningReport) -> None:
        override = OverrideEntry(
            category="5.1.z",
            verdict_before="amber",
            verdict_after="clear",
            rationale="Invalid category.",
            approver="X",
            approver_email="x@example.org",
            approved_at=datetime(2026, 4, 16, tzinfo=UTC),
        )
        result = apply_overrides(amber_report, [override])
        assert len(result.overrides_applied) == 0
