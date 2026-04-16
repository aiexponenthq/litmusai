"""Unit tests for the Ruleset model + optional signature block (FR-23, FR-34)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from litmusai.models import Rule, Ruleset, RulesetSignature


def _sample_rule(rule_id: str = "rule_a_influences_behaviour") -> Rule:
    return Rule(
        id=rule_id,
        category="5.1.a",
        version="v1",
        description="System attempts to influence user behaviour.",
        expression="system.outputs.behaviour_predictions == true",
        verdict_if_triggered="amber",
        confidence_delta=None,
        citations=["Art. 5(1)(a)", "Recital 29"],
        reviewed_by="aiexponent-internal-panel-v1",
        reviewed_date="2026-04-15",
    )


class TestRule:
    def test_valid_rule(self) -> None:
        rule = _sample_rule()
        assert rule.id == "rule_a_influences_behaviour"
        assert rule.category == "5.1.a"
        assert rule.verdict_if_triggered == "amber"

    @pytest.mark.parametrize("verdict", ["clear", "amber", "red"])
    def test_accepts_valid_verdicts(self, verdict: str) -> None:
        rule = Rule(
            id=f"r_{verdict}",
            category="5.1.a",
            version="v1",
            description="…",
            expression="true",
            verdict_if_triggered=verdict,  # type: ignore[arg-type]
            citations=["Art. 5"],
            reviewed_by="aiexponent-internal-panel-v1",
            reviewed_date="2026-04-15",
        )
        assert rule.verdict_if_triggered == verdict

    def test_rejects_invalid_verdict(self) -> None:
        with pytest.raises(ValidationError):
            Rule(
                id="x",
                category="5.1.a",
                version="v1",
                description="…",
                expression="true",
                verdict_if_triggered="green",  # type: ignore[arg-type]
                citations=[],
                reviewed_by="panel",
                reviewed_date="2026-04-15",
            )

    def test_rule_id_must_match_snake_case(self) -> None:
        with pytest.raises(ValidationError):
            Rule(
                id="Invalid Rule ID With Spaces",
                category="5.1.a",
                version="v1",
                description="…",
                expression="true",
                verdict_if_triggered="amber",
                citations=[],
                reviewed_by="panel",
                reviewed_date="2026-04-15",
            )

    def test_category_must_match_article_5_pattern(self) -> None:
        with pytest.raises(ValidationError):
            Rule(
                id="x",
                category="article-5",
                version="v1",
                description="…",
                expression="true",
                verdict_if_triggered="amber",
                citations=[],
                reviewed_by="panel",
                reviewed_date="2026-04-15",
            )

    @pytest.mark.parametrize("cat", ["5.1.a", "5.1.b", "5.1.c", "5.1.d", "5.1.e", "5.1.f", "5.1.g", "5.1.h"])
    def test_accepts_all_article_5_categories(self, cat: str) -> None:
        rule = Rule(
            id="r",
            category=cat,
            version="v1",
            description="…",
            expression="true",
            verdict_if_triggered="amber",
            citations=[f"Art. {cat}"],
            reviewed_by="panel",
            reviewed_date="2026-04-15",
        )
        assert rule.category == cat


class TestRulesetSignature:
    def test_unsigned_ruleset_has_no_signature(self) -> None:
        rs = Ruleset(
            ruleset_version="ruleset-2024-1689-v1.0",
            regulation="Regulation (EU) 2024/1689",
            effective_date="2025-02-02",
            rules=[_sample_rule()],
            signature=None,
        )
        assert rs.signature is None

    def test_signed_ruleset_sha256(self) -> None:
        sig = RulesetSignature(
            signer_name="Smith & Co LLP",
            signer_bar_number="BAR-12345",
            signer_firm="Smith & Co LLP",
            signer_email="partners@smithco.example",
            signed_date="2026-05-01",
            signature_algorithm="sha256",
            signature_value="deadbeef" * 8,
        )
        rs = Ruleset(
            ruleset_version="acme-corp-v1.0",
            regulation="Regulation (EU) 2024/1689",
            effective_date="2025-02-02",
            rules=[_sample_rule()],
            signature=sig,
        )
        assert rs.signature is not None
        assert rs.signature.signer_name == "Smith & Co LLP"
        assert rs.signature.signature_algorithm == "sha256"

    @pytest.mark.parametrize("alg", ["sha256", "pgp-detached", "x509-pkcs7"])
    def test_accepts_all_whitelisted_algorithms(self, alg: str) -> None:
        sig = RulesetSignature(
            signer_name="x",
            signer_email="x@example.org",
            signed_date="2026-05-01",
            signature_algorithm=alg,  # type: ignore[arg-type]
            signature_value="00",
        )
        assert sig.signature_algorithm == alg

    def test_rejects_unknown_algorithm(self) -> None:
        with pytest.raises(ValidationError):
            RulesetSignature(
                signer_name="x",
                signer_email="x@example.org",
                signed_date="2026-05-01",
                signature_algorithm="md5",  # type: ignore[arg-type]
                signature_value="00",
            )

    def test_rejects_missing_signer_name(self) -> None:
        with pytest.raises(ValidationError):
            RulesetSignature(
                signer_email="x@example.org",
                signed_date="2026-05-01",
                signature_algorithm="sha256",
                signature_value="00",
            )  # type: ignore[call-arg]


class TestRuleset:
    def test_empty_rules_list_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Ruleset(
                ruleset_version="ruleset-2024-1689-v1.0",
                regulation="Regulation (EU) 2024/1689",
                effective_date="2025-02-02",
                rules=[],
                signature=None,
            )

    def test_ruleset_roundtrip(self) -> None:
        rs = Ruleset(
            ruleset_version="ruleset-2024-1689-v1.0",
            regulation="Regulation (EU) 2024/1689",
            effective_date="2025-02-02",
            rules=[_sample_rule()],
            signature=None,
        )
        as_json = rs.model_dump_json()
        reparsed = Ruleset.model_validate_json(as_json)
        assert reparsed.rules[0].id == "rule_a_influences_behaviour"

    def test_rule_ids_must_be_unique(self) -> None:
        dup = _sample_rule()
        with pytest.raises(ValidationError):
            Ruleset(
                ruleset_version="x",
                regulation="Regulation (EU) 2024/1689",
                effective_date="2025-02-02",
                rules=[dup, _sample_rule()],
                signature=None,
            )
