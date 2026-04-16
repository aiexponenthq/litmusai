"""Unit tests for the ScreeningReport output model.

Pinned to PRD §7.2 (Output models), FR-16 (report JSON shape), FR-19 (hash),
FR-36 (ruleset provenance header), NFR-6 (determinism).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from litmusai.models import (
    CategoryResult,
    Citation,
    OverrideEntry,
    ReportSummary,
    RulesetProvenance,
    ScreeningReport,
    SystemDescription,
)

ALL_CATEGORIES = [
    "5.1.a",
    "5.1.b",
    "5.1.c",
    "5.1.d",
    "5.1.e",
    "5.1.f",
    "5.1.g",
    "5.1.h",
]


def _sample_category_result(verdict: str = "clear") -> CategoryResult:
    return CategoryResult(
        label="Test Category",
        verdict=verdict,  # type: ignore[arg-type]
        confidence="high",
        rationale="Sample rationale for unit test.",
        triggered_rules=[],
        regulation_citations=[Citation(article="Art. 5(1)(a)", recital="Recital 29")],
        remediation=[],
    )


class TestCitation:
    def test_article_required(self) -> None:
        cit = Citation(article="Art. 5(1)(c)")
        assert cit.article == "Art. 5(1)(c)"
        assert cit.recital is None

    def test_article_and_recital(self) -> None:
        cit = Citation(article="Art. 5(1)(f)", recital="Recital 44")
        assert cit.recital == "Recital 44"

    def test_rejects_empty_article(self) -> None:
        with pytest.raises(ValidationError):
            Citation(article="")


class TestCategoryResult:
    @pytest.mark.parametrize("verdict", ["clear", "amber", "red"])
    def test_accepts_valid_verdicts(self, verdict: str) -> None:
        result = _sample_category_result(verdict=verdict)
        assert result.verdict == verdict

    def test_rejects_invalid_verdict(self) -> None:
        with pytest.raises(ValidationError):
            _sample_category_result(verdict="green")

    @pytest.mark.parametrize("confidence", ["high", "medium", "low"])
    def test_accepts_valid_confidence(self, confidence: str) -> None:
        result = CategoryResult(
            label="x",
            verdict="clear",
            confidence=confidence,  # type: ignore[arg-type]
            rationale="y",
            triggered_rules=[],
            regulation_citations=[Citation(article="Art. 5(1)(a)")],
            remediation=[],
        )
        assert result.confidence == confidence

    def test_rejects_invalid_confidence(self) -> None:
        with pytest.raises(ValidationError):
            CategoryResult(
                label="x",
                verdict="clear",
                confidence="maybe",  # type: ignore[arg-type]
                rationale="y",
                triggered_rules=[],
                regulation_citations=[Citation(article="Art. 5(1)(a)")],
                remediation=[],
            )

    def test_triggered_rules_default_empty(self) -> None:
        result = _sample_category_result()
        assert result.triggered_rules == []

    def test_rationale_required(self) -> None:
        with pytest.raises(ValidationError):
            CategoryResult(
                label="x",
                verdict="clear",
                confidence="high",
                rationale="",
                triggered_rules=[],
                regulation_citations=[Citation(article="Art. 5(1)(a)")],
                remediation=[],
            )


class TestReportSummary:
    def test_valid_summary(self) -> None:
        s = ReportSummary(
            overall_verdict="amber",
            red_count=0,
            amber_count=2,
            clear_count=6,
            requires_legal_review=True,
            highest_penalty_exposure="€35M or 7% global turnover (Art. 99(3))",
        )
        assert s.amber_count == 2
        assert s.red_count + s.amber_count + s.clear_count == 8

    def test_negative_count_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ReportSummary(
                overall_verdict="clear",
                red_count=-1,
                amber_count=0,
                clear_count=8,
                requires_legal_review=False,
                highest_penalty_exposure="",
            )


class TestRulesetProvenance:
    def test_unreviewed_reference_ruleset(self) -> None:
        p = RulesetProvenance(
            ruleset_version="ruleset-2024-1689-v1.0",
            regulation="Regulation (EU) 2024/1689",
            effective_date="2025-02-02",
            signer_name=None,
            signed_date=None,
            signature_status="unsigned",
            display_label="aiexponent-reference-v1.0 (UNREVIEWED — internal panel authored, no external legal review)",
        )
        assert p.signature_status == "unsigned"
        assert "UNREVIEWED" in p.display_label

    def test_signed_ruleset(self) -> None:
        p = RulesetProvenance(
            ruleset_version="acme-corp-v1.0",
            regulation="Regulation (EU) 2024/1689",
            effective_date="2025-02-02",
            signer_name="Smith & Co LLP",
            signed_date="2026-05-01",
            signature_status="verified",
            display_label="acme-corp-v1.0 (SIGNED by: Smith & Co LLP · 2026-05-01 · signature verified)",
        )
        assert p.signature_status == "verified"
        assert p.signer_name == "Smith & Co LLP"

    def test_invalid_signature_status_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RulesetProvenance(
                ruleset_version="x",
                regulation="y",
                effective_date="2025-02-02",
                signer_name=None,
                signed_date=None,
                signature_status="maybe-valid",  # type: ignore[arg-type]
                display_label="x",
            )


class TestScreeningReport:
    def _make_report(
        self, minimal_system_dict: dict[str, Any], fixed_timestamp: datetime
    ) -> ScreeningReport:
        system = SystemDescription(**minimal_system_dict)
        categories = {cat: _sample_category_result() for cat in ALL_CATEGORIES}
        return ScreeningReport(
            report_version="1.0",
            ruleset_version="ruleset-2024-1689-v1.0",
            litmusai_version="0.1.0",
            generated_at=fixed_timestamp,
            input_hash_sha256="a" * 64,
            system=system,
            categories=categories,
            summary=ReportSummary(
                overall_verdict="clear",
                red_count=0,
                amber_count=0,
                clear_count=8,
                requires_legal_review=False,
                highest_penalty_exposure="€35M or 7% global turnover (Art. 99(3))",
            ),
            ruleset_provenance=RulesetProvenance(
                ruleset_version="ruleset-2024-1689-v1.0",
                regulation="Regulation (EU) 2024/1689",
                effective_date="2025-02-02",
                signer_name=None,
                signed_date=None,
                signature_status="unsigned",
                display_label=(
                    "aiexponent-reference-v1.0 (UNREVIEWED — internal panel authored, "
                    "no external legal review)"
                ),
            ),
            disclaimers=[
                "This is a screening tool, not legal advice.",
                "LitmusAI is not a notified body.",
            ],
            overrides_applied=[],
        )

    def test_builds_valid_report(
        self, minimal_system_dict: dict[str, Any], fixed_timestamp: datetime
    ) -> None:
        report = self._make_report(minimal_system_dict, fixed_timestamp)
        assert report.report_version == "1.0"
        assert len(report.categories) == 8
        assert report.input_hash_sha256 == "a" * 64

    def test_requires_all_eight_categories(
        self, minimal_system_dict: dict[str, Any], fixed_timestamp: datetime
    ) -> None:
        report = self._make_report(minimal_system_dict, fixed_timestamp)
        assert set(report.categories.keys()) == set(ALL_CATEGORIES)

    def test_hash_must_be_64_hex_chars(
        self, minimal_system_dict: dict[str, Any], fixed_timestamp: datetime
    ) -> None:
        report = self._make_report(minimal_system_dict, fixed_timestamp)
        data = report.model_dump()
        data["input_hash_sha256"] = "notahash"
        with pytest.raises(ValidationError):
            ScreeningReport.model_validate(data)

    def test_json_roundtrip(
        self, minimal_system_dict: dict[str, Any], fixed_timestamp: datetime
    ) -> None:
        report = self._make_report(minimal_system_dict, fixed_timestamp)
        as_json = report.model_dump_json()
        reparsed = ScreeningReport.model_validate_json(as_json)
        assert reparsed.ruleset_provenance.signature_status == "unsigned"
        assert reparsed.summary.clear_count == 8

    def test_overrides_default_empty(
        self, minimal_system_dict: dict[str, Any], fixed_timestamp: datetime
    ) -> None:
        report = self._make_report(minimal_system_dict, fixed_timestamp)
        assert report.overrides_applied == []

    def test_disclaimers_required_non_empty(
        self, minimal_system_dict: dict[str, Any], fixed_timestamp: datetime
    ) -> None:
        report = self._make_report(minimal_system_dict, fixed_timestamp)
        assert len(report.disclaimers) >= 1


class TestOverrideEntry:
    def test_valid_override(self) -> None:
        o = OverrideEntry(
            category="5.1.a",
            verdict_before="amber",
            verdict_after="clear",
            rationale="Legal team confirmed no subliminal techniques present.",
            approver="Jane Counsel",
            approver_email="jane@example.org",
            approved_at=datetime(2026, 4, 15, tzinfo=UTC),
        )
        assert o.verdict_before == "amber"
        assert o.approver_email == "jane@example.org"

    def test_rejects_invalid_email(self) -> None:
        with pytest.raises(ValidationError):
            OverrideEntry(
                category="5.1.a",
                verdict_before="amber",
                verdict_after="clear",
                rationale="…",
                approver="x",
                approver_email="not-an-email",
                approved_at=datetime(2026, 4, 15, tzinfo=UTC),
            )
