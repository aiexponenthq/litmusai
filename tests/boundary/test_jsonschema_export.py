"""Boundary tests: exported JSON Schemas round-trip through jsonschema.validate.

Pinned to PRD §8.1 (schemas published in _data/schemas/) and FR-1.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from litmusai.models import Ruleset, ScreeningReport, SystemDescription

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "src" / "litmusai" / "_data" / "schemas"


def _load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / name
    assert path.exists(), f"Schema file missing: {path}"
    return json.loads(path.read_text())


def _export_schema() -> None:
    """Generate JSON Schemas from Pydantic models and write to _data/schemas/."""
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for model, filename in [
        (SystemDescription, "system-description.schema.json"),
        (ScreeningReport, "screening-report.schema.json"),
        (Ruleset, "ruleset.schema.json"),
    ]:
        schema = model.model_json_schema()
        (SCHEMA_DIR / filename).write_text(json.dumps(schema, indent=2) + "\n")


@pytest.fixture(autouse=True, scope="module")
def _ensure_schemas_exported() -> None:
    _export_schema()


class TestSystemDescriptionSchema:
    def test_schema_file_exists(self) -> None:
        assert (SCHEMA_DIR / "system-description.schema.json").exists()

    def test_minimal_valid_payload_validates(self, minimal_system_dict: dict[str, Any]) -> None:
        schema = _load_schema("system-description.schema.json")
        jsonschema.validate(instance=minimal_system_dict, schema=schema)

    def test_missing_required_field_fails_validation(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        del minimal_system_dict["name"]
        schema = _load_schema("system-description.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=minimal_system_dict, schema=schema)


class TestScreeningReportSchema:
    def test_schema_file_exists(self) -> None:
        assert (SCHEMA_DIR / "screening-report.schema.json").exists()


class TestRulesetSchema:
    def test_schema_file_exists(self) -> None:
        assert (SCHEMA_DIR / "ruleset.schema.json").exists()
