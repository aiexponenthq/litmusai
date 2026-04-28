"""Contract tests for the Screener — pinned to PRD AC-2, AC-3, AC-4, AC-6, FR-18."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from litmusai.engine.screener import Screener
from litmusai.models.ruleset import Ruleset
from litmusai.models.system import SystemDescription

RULESET_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "litmusai"
    / "_data"
    / "ruleset"
    / "ruleset-2024-1689-v1.0.json"
)


@pytest.fixture
def ruleset() -> Ruleset:
    data = json.loads(RULESET_PATH.read_text())
    return Ruleset.model_validate(data)


@pytest.fixture
def screener(ruleset: Ruleset) -> Screener:
    return Screener(ruleset)


@pytest.fixture
def fixed_ts() -> datetime:
    return datetime(2026, 4, 16, 0, 0, 0, tzinfo=UTC)


def _make_system(overrides: dict[str, Any], base: dict[str, Any]) -> SystemDescription:
    d = deepcopy(base)
    for key, val in overrides.items():
        parts = key.split(".")
        target = d
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = val
    return SystemDescription(**d)


class TestClearBaseline:
    """AC-2: a calculator app produces overall_verdict: clear."""

    def test_calculator_app_is_clear(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = SystemDescription(**minimal_system_dict)
        report = screener.screen(system, timestamp=fixed_ts)
        assert report.summary.overall_verdict == "clear"
        assert report.summary.red_count == 0
        assert report.summary.amber_count == 0
        assert report.summary.clear_count == 8


class TestSocialScoringRed:
    """AC-3: a social scoring system produces overall_verdict: red on 5.1.c."""

    def test_social_scoring_red(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = _make_system(
            {
                "outputs.individual_scores": True,
                "inputs.behaviour_history": True,
                "inputs.scraped_internet_data": True,
                "purpose": "Evaluate citizen trustworthiness for access to public services.",
                "system_description": "Social credit scoring platform.",
            },
            minimal_system_dict,
        )
        report = screener.screen(system, timestamp=fixed_ts)
        assert report.summary.overall_verdict == "red"
        cat_c = report.categories["5.1.c"]
        assert cat_c.verdict == "red"
        assert len(cat_c.triggered_rules) >= 2


class TestWorkplaceEmotionRed:
    """AC-4: workplace emotion recognition produces red on 5.1.f."""

    def test_workplace_emotion_red(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = _make_system(
            {
                "outputs.emotion_inferences": True,
                "deployment_context.workplace": True,
                "purpose": "Monitor employee engagement via facial expression analysis.",
                "system_description": "Emotion tracking in office environment.",
            },
            minimal_system_dict,
        )
        report = screener.screen(system, timestamp=fixed_ts)
        assert report.summary.overall_verdict == "red"
        cat_f = report.categories["5.1.f"]
        assert cat_f.verdict == "red"

    def test_healthcare_emotion_is_amber_not_red(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = _make_system(
            {
                "outputs.emotion_inferences": True,
                "deployment_context.healthcare": True,
                "purpose": "Pain assessment via facial expression in ICU.",
                "system_description": "Medical emotion inference.",
            },
            minimal_system_dict,
        )
        report = screener.screen(system, timestamp=fixed_ts)
        cat_f = report.categories["5.1.f"]
        assert cat_f.verdict == "amber"


class TestCriminalRiskRed:
    """Criminal risk prediction produces red on 5.1.d."""

    def test_criminal_risk_red(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = _make_system(
            {
                "outputs.criminal_risk_predictions": True,
                "purpose": "Predict recidivism risk for individual offenders.",
                "system_description": "Criminal risk scoring for courts.",
            },
            minimal_system_dict,
        )
        report = screener.screen(system, timestamp=fixed_ts)
        assert report.summary.overall_verdict == "red"
        assert report.categories["5.1.d"].verdict == "red"


class TestMinorsTargeting:
    """Targeting minors with behaviour predictions produces red on 5.1.b."""

    def test_minors_behaviour_prediction_red(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = _make_system(
            {
                "subject_population.categories": ["minors"],
                "outputs.behaviour_predictions": True,
                "purpose": "Predict teenager engagement for social media feed ranking.",
                "system_description": "Youth engagement predictor.",
            },
            minimal_system_dict,
        )
        report = screener.screen(system, timestamp=fixed_ts)
        assert report.categories["5.1.b"].verdict == "red"


class TestDeterminism:
    """AC-6: same input twice produces identical reports (modulo generated_at)."""

    def test_deterministic_output(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = SystemDescription(**minimal_system_dict)
        r1 = screener.screen(system, timestamp=fixed_ts)
        r2 = screener.screen(system, timestamp=fixed_ts)
        assert r1.model_dump_json() == r2.model_dump_json()


class TestReportShape:
    """FR-18: overall verdict follows worst-case aggregation."""

    def test_any_red_makes_overall_red(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = _make_system(
            {"outputs.criminal_risk_predictions": True},
            minimal_system_dict,
        )
        report = screener.screen(system, timestamp=fixed_ts)
        assert report.summary.overall_verdict == "red"
        assert report.summary.requires_legal_review is True

    def test_hash_present_and_deterministic(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = SystemDescription(**minimal_system_dict)
        r = screener.screen(system, timestamp=fixed_ts)
        assert len(r.input_hash_sha256) == 64
        r2 = screener.screen(system, timestamp=fixed_ts)
        assert r.input_hash_sha256 == r2.input_hash_sha256

    def test_disclaimers_present(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = SystemDescription(**minimal_system_dict)
        r = screener.screen(system, timestamp=fixed_ts)
        assert len(r.disclaimers) >= 3
        assert any("not legal advice" in d.lower() for d in r.disclaimers)

    def test_provenance_unsigned(
        self,
        screener: Screener,
        minimal_system_dict: dict[str, Any],
        fixed_ts: datetime,
    ) -> None:
        system = SystemDescription(**minimal_system_dict)
        r = screener.screen(system, timestamp=fixed_ts)
        assert r.ruleset_provenance.signature_status == "unsigned"
        assert "UNREVIEWED" in r.ruleset_provenance.display_label
