"""Security tests for the expression interpreter.

These tests verify that the expression engine CANNOT be used for arbitrary
code execution. This is the single most critical test file in the project.
Pinned to PRD section 8.4 + NFR-12.

NOTE: strings below are test INPUTS that must be REJECTED by the interpreter.
They are never executed as Python code.
"""

from __future__ import annotations

from typing import ClassVar

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from litmusai.engine.expression import ExpressionError, evaluate


@pytest.fixture
def safe_ctx() -> dict:
    return {
        "system": {
            "name": "Test",
            "inputs": {"biometric": False},
            "outputs": {"individual_scores": False},
            "deployment_context": {"workplace": False},
            "subject_population": {"categories": ["general_public"]},
            "deployment_jurisdictions": ["EU"],
            "output_consumed_in_eu": True,
            "mitigations": [],
            "purpose": "test",
        }
    }


class TestCodeInjectionPrevention:
    """Every test here asserts that the interpreter REJECTS the expression."""

    DANGEROUS_EXPRESSIONS: ClassVar[list[str]] = [
        "__import__('os')",
        "globals()",
        "locals()",
        "getattr(system, 'name')",
        "setattr(system, 'name', 'hacked')",
        "open('/etc/passwd')",
        "compile('1', '', 'single')",
        "type('X', (), {})",
        "lambda: 1",
        "true; import os",
        "x = 1",
        "[x for x in range(10)]",
        "{k: v for k, v in {}.items()}",
        'system["name"]',
        "system.name[0:2]",
        "(x := 1)",
        "await something()",
        "yield 1",
        "*system.mitigations",
        "2 ** 64",
        "system.__class__",
        "__builtins__",
        "system.__class__.__mro__",
        "system.__class__.__subclasses__()",
        "breakpoint()",
        "dir()",
        "vars()",
        "id(system)",
        "hash(system)",
        "delattr(system, 'name')",
        "isinstance(system, dict)",
        "issubclass(dict, object)",
    ]

    @pytest.mark.parametrize("expr", DANGEROUS_EXPRESSIONS)
    def test_rejects_dangerous_expression(self, expr: str, safe_ctx: dict) -> None:
        with pytest.raises(ExpressionError):
            evaluate(expr, safe_ctx)


class TestHypothesisFuzz:
    @given(expr=st.text(min_size=1, max_size=200))
    @settings(
        max_examples=10000,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_arbitrary_strings_never_escape_sandbox(self, expr: str, safe_ctx: dict) -> None:
        """Any random string must either return a safe value or raise ExpressionError.
        Any other exception type means the sandbox has been breached."""
        try:
            result = evaluate(expr, safe_ctx)
            assert isinstance(result, (bool, str, int, float, list, dict, type(None)))
        except ExpressionError:
            pass
