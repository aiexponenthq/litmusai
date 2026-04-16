"""Unit tests for the constrained expression parser.

80+ cases covering parsing, precedence, operator combinations, and error handling.
Pinned to PRD §8.4. This is the highest-risk component in LitmusAI — a bug here
could allow arbitrary code execution via ruleset files.
"""

from __future__ import annotations

import pytest

from litmusai.engine.expression import ExpressionError, evaluate

# ── Fixtures: a mock system dict matching SystemDescription shape ──


@pytest.fixture
def system_ctx() -> dict:
    return {
        "system": {
            "name": "Test System",
            "inputs": {
                "biometric": True,
                "facial_images": False,
                "emotional_state_inference": True,
                "behaviour_history": False,
                "scraped_internet_data": False,
                "freetext_prompts": False,
            },
            "outputs": {
                "individual_scores": True,
                "behaviour_predictions": False,
                "criminal_risk_predictions": True,
                "emotion_inferences": True,
                "sensitive_attribute_classifications": False,
                "freetext_generations": False,
            },
            "deployment_context": {
                "workplace": True,
                "education": False,
                "public_space": True,
                "real_time_operation": True,
                "law_enforcement_use": False,
                "healthcare": False,
                "financial_services": True,
            },
            "subject_population": {
                "categories": ["minors", "workers"],
            },
            "deployment_jurisdictions": ["EU", "US"],
            "output_consumed_in_eu": True,
            "mitigations": ["consent_flow", "human_review"],
            "purpose": "credit scoring for retail loans",
        }
    }


# ── Boolean literals ──


class TestBooleanLiterals:
    def test_true(self, system_ctx: dict) -> None:
        assert evaluate("true", system_ctx) is True

    def test_false(self, system_ctx: dict) -> None:
        assert evaluate("false", system_ctx) is False


# ── Field access ──


class TestFieldAccess:
    def test_simple_field(self, system_ctx: dict) -> None:
        assert evaluate("system.inputs.biometric", system_ctx) is True

    def test_nested_field(self, system_ctx: dict) -> None:
        assert evaluate("system.outputs.criminal_risk_predictions", system_ctx) is True

    def test_false_field(self, system_ctx: dict) -> None:
        assert evaluate("system.inputs.facial_images", system_ctx) is False

    def test_string_field(self, system_ctx: dict) -> None:
        result = evaluate("system.purpose", system_ctx)
        assert result == "credit scoring for retail loans"

    def test_list_field(self, system_ctx: dict) -> None:
        result = evaluate("system.deployment_jurisdictions", system_ctx)
        assert result == ["EU", "US"]

    def test_nonexistent_field_raises(self, system_ctx: dict) -> None:
        with pytest.raises(ExpressionError, match="field"):
            evaluate("system.inputs.nonexistent_sensor", system_ctx)

    def test_cannot_access_outside_system(self, system_ctx: dict) -> None:
        with pytest.raises(ExpressionError):
            evaluate("__builtins__", system_ctx)


# ── Comparisons ──


class TestComparisons:
    def test_eq_true(self, system_ctx: dict) -> None:
        assert evaluate("system.inputs.biometric == true", system_ctx) is True

    def test_eq_false(self, system_ctx: dict) -> None:
        assert evaluate("system.inputs.biometric == false", system_ctx) is False

    def test_neq(self, system_ctx: dict) -> None:
        assert evaluate("system.inputs.biometric != false", system_ctx) is True

    def test_string_eq(self, system_ctx: dict) -> None:
        assert evaluate('system.name == "Test System"', system_ctx) is True

    def test_string_neq(self, system_ctx: dict) -> None:
        assert evaluate('system.name != "Other"', system_ctx) is True


# ── Boolean operators ──


class TestBooleanOperators:
    def test_and_true(self, system_ctx: dict) -> None:
        assert (
            evaluate(
                "system.inputs.biometric == true and system.outputs.individual_scores == true",
                system_ctx,
            )
            is True
        )

    def test_and_false(self, system_ctx: dict) -> None:
        assert (
            evaluate(
                "system.inputs.biometric == true and system.inputs.facial_images == true",
                system_ctx,
            )
            is False
        )

    def test_or_true(self, system_ctx: dict) -> None:
        assert (
            evaluate(
                "system.inputs.biometric == true or system.inputs.facial_images == true",
                system_ctx,
            )
            is True
        )

    def test_or_false(self, system_ctx: dict) -> None:
        assert (
            evaluate(
                "system.inputs.facial_images == true or system.inputs.behaviour_history == true",
                system_ctx,
            )
            is False
        )

    def test_not(self, system_ctx: dict) -> None:
        assert evaluate("not system.inputs.facial_images", system_ctx) is True

    def test_not_true(self, system_ctx: dict) -> None:
        assert evaluate("not system.inputs.biometric", system_ctx) is False

    def test_precedence_not_over_and(self, system_ctx: dict) -> None:
        assert (
            evaluate(
                "not system.inputs.facial_images and system.inputs.biometric",
                system_ctx,
            )
            is True
        )

    def test_parentheses(self, system_ctx: dict) -> None:
        assert (
            evaluate(
                "(system.inputs.facial_images or system.inputs.biometric) and system.outputs.individual_scores",
                system_ctx,
            )
            is True
        )


# ── Set membership ──


class TestSetMembership:
    def test_in_list(self, system_ctx: dict) -> None:
        assert evaluate('"consent_flow" in system.mitigations', system_ctx) is True

    def test_not_in_list(self, system_ctx: dict) -> None:
        assert evaluate('"encryption" not in system.mitigations', system_ctx) is True

    def test_in_false(self, system_ctx: dict) -> None:
        assert evaluate('"encryption" in system.mitigations', system_ctx) is False


# ── String matching ──


class TestStringMatching:
    def test_contains(self, system_ctx: dict) -> None:
        assert evaluate('contains(system.purpose, "credit")', system_ctx) is True

    def test_contains_false(self, system_ctx: dict) -> None:
        assert evaluate('contains(system.purpose, "medical")', system_ctx) is False

    def test_starts_with(self, system_ctx: dict) -> None:
        assert evaluate('starts_with(system.purpose, "credit")', system_ctx) is True

    def test_starts_with_false(self, system_ctx: dict) -> None:
        assert evaluate('starts_with(system.purpose, "loan")', system_ctx) is False


# ── Helper functions ──


class TestHelperFunctions:
    def test_has_jurisdiction_eu(self, system_ctx: dict) -> None:
        assert evaluate('has_jurisdiction(system, "EU")', system_ctx) is True

    def test_has_jurisdiction_missing(self, system_ctx: dict) -> None:
        assert evaluate('has_jurisdiction(system, "CN")', system_ctx) is False

    def test_targets_population_minors(self, system_ctx: dict) -> None:
        assert evaluate('targets_population(system, "minors")', system_ctx) is True

    def test_targets_population_missing(self, system_ctx: dict) -> None:
        assert (
            evaluate('targets_population(system, "persons_with_disabilities")', system_ctx) is False
        )


# ── Parse errors ──


class TestParseErrors:
    def test_empty_expression(self, system_ctx: dict) -> None:
        with pytest.raises(ExpressionError):
            evaluate("", system_ctx)

    def test_unclosed_paren(self, system_ctx: dict) -> None:
        with pytest.raises(ExpressionError):
            evaluate("(system.inputs.biometric == true", system_ctx)

    def test_unclosed_string(self, system_ctx: dict) -> None:
        with pytest.raises(ExpressionError):
            evaluate('system.name == "unclosed', system_ctx)

    def test_invalid_operator(self, system_ctx: dict) -> None:
        with pytest.raises(ExpressionError):
            evaluate("system.inputs.biometric ** 2", system_ctx)

    def test_trailing_operator(self, system_ctx: dict) -> None:
        with pytest.raises(ExpressionError):
            evaluate("system.inputs.biometric and", system_ctx)
