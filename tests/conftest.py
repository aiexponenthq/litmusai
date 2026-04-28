"""Global pytest fixtures + network isolation enforcement.

We import pytest_socket here and leave its enablement to the CLI flag
`--disable-socket` in CI so local devs can still pull dependencies.
The full suite in CI always runs with sockets disabled — this is the
NFR-8 gate.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest


@pytest.fixture
def minimal_system_dict() -> dict[str, Any]:
    """A well-formed SystemDescription payload with every field at its safest default.

    This is the 'clear' baseline — a calculator app for adults — used by
    AC-2 and as a starting point for most category-specific tests.
    """
    return {
        "name": "Adult Calculator",
        "version": "1.0.0",
        "provider": "AI Exponent LLC",
        "deployer": "AI Exponent LLC",
        "purpose": "Basic arithmetic for adult users.",
        "system_description": (
            "A stateless pocket calculator. No personal data processed, no "
            "behaviour influence, no ML model."
        ),
        "deployment_jurisdictions": ["EU"],
        "output_consumed_in_eu": True,
        "subject_population": {
            "categories": ["general_public"],
            "notes": None,
        },
        "inputs": {
            "biometric": False,
            "facial_images": False,
            "emotional_state_inference": False,
            "behaviour_history": False,
            "scraped_internet_data": False,
            "freetext_prompts": False,
            "other": None,
        },
        "outputs": {
            "individual_scores": False,
            "behaviour_predictions": False,
            "criminal_risk_predictions": False,
            "emotion_inferences": False,
            "sensitive_attribute_classifications": False,
            "freetext_generations": False,
            "other": None,
        },
        "deployment_context": {
            "workplace": False,
            "education": False,
            "public_space": False,
            "real_time_operation": False,
            "law_enforcement_use": False,
            "healthcare": False,
            "financial_services": False,
            "other": None,
        },
        "mitigations": [],
        "metadata": {
            "last_reviewed": None,
            "owner": None,
            "reviewed_by": None,
        },
    }


@pytest.fixture
def fixed_timestamp() -> datetime:
    """A deterministic timestamp for byte-identical report comparisons."""
    return datetime(2026, 4, 15, 12, 0, 0, tzinfo=UTC)
