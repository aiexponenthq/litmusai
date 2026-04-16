"""Unit tests for the SystemDescription input model.

Pinned to PRD §7.1 (Input models) and FR-1 (Pydantic input schema).
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from litmusai.models import (
    DeploymentContext,
    Metadata,
    SubjectPopulation,
    SystemDescription,
    SystemInputs,
    SystemOutputs,
)


class TestSubjectPopulation:
    def test_accepts_single_general_public_category(self) -> None:
        sp = SubjectPopulation(categories=["general_public"])
        assert sp.categories == ["general_public"]
        assert sp.notes is None

    def test_accepts_multiple_categories(self) -> None:
        sp = SubjectPopulation(categories=["minors", "students"])
        assert "minors" in sp.categories
        assert "students" in sp.categories

    def test_accepts_all_enumerated_categories(self) -> None:
        every = [
            "general_public",
            "minors",
            "workers",
            "students",
            "persons_with_disabilities",
            "persons_in_vulnerable_economic_situations",
            "other",
        ]
        sp = SubjectPopulation(categories=every)
        assert len(sp.categories) == 7

    def test_rejects_empty_categories_list(self) -> None:
        with pytest.raises(ValidationError):
            SubjectPopulation(categories=[])

    def test_rejects_unknown_category_value(self) -> None:
        with pytest.raises(ValidationError):
            SubjectPopulation(categories=["martians"])

    def test_notes_optional_string(self) -> None:
        sp = SubjectPopulation(categories=["minors"], notes="ages 13-17")
        assert sp.notes == "ages 13-17"


class TestSystemInputs:
    def test_defaults_all_false(self) -> None:
        inputs = SystemInputs()
        for flag in (
            "biometric",
            "facial_images",
            "emotional_state_inference",
            "behaviour_history",
            "scraped_internet_data",
            "freetext_prompts",
        ):
            assert getattr(inputs, flag) is False

    def test_individual_flag_set_true(self) -> None:
        inputs = SystemInputs(biometric=True)
        assert inputs.biometric is True
        assert inputs.facial_images is False

    def test_rejects_unknown_field_under_strict_mode(self) -> None:
        with pytest.raises(ValidationError):
            SystemInputs(unknown_sensor=True)  # type: ignore[call-arg]

    def test_other_accepts_free_text(self) -> None:
        inputs = SystemInputs(other="heart rate via wearable")
        assert inputs.other == "heart rate via wearable"


class TestSystemOutputs:
    def test_defaults_all_false(self) -> None:
        outputs = SystemOutputs()
        assert outputs.individual_scores is False
        assert outputs.behaviour_predictions is False
        assert outputs.criminal_risk_predictions is False
        assert outputs.emotion_inferences is False
        assert outputs.sensitive_attribute_classifications is False
        assert outputs.freetext_generations is False

    def test_individual_flag_set_true(self) -> None:
        outputs = SystemOutputs(individual_scores=True)
        assert outputs.individual_scores is True


class TestDeploymentContext:
    def test_defaults_all_false(self) -> None:
        ctx = DeploymentContext()
        assert ctx.workplace is False
        assert ctx.law_enforcement_use is False
        assert ctx.healthcare is False

    def test_workplace_and_emotion_combo(self) -> None:
        ctx = DeploymentContext(workplace=True)
        assert ctx.workplace is True


class TestMetadata:
    def test_all_fields_optional(self) -> None:
        m = Metadata()
        assert m.owner is None
        assert m.last_reviewed is None
        assert m.reviewed_by is None


class TestSystemDescription:
    def test_minimal_valid_payload(self, minimal_system_dict: dict[str, Any]) -> None:
        system = SystemDescription(**minimal_system_dict)
        assert system.name == "Adult Calculator"
        assert system.version == "1.0.0"
        assert system.deployment_jurisdictions == ["EU"]
        assert system.output_consumed_in_eu is True
        assert system.mitigations == []
        assert system.subject_population.categories == ["general_public"]

    def test_missing_required_name_raises(self, minimal_system_dict: dict[str, Any]) -> None:
        del minimal_system_dict["name"]
        with pytest.raises(ValidationError) as exc:
            SystemDescription(**minimal_system_dict)
        assert "name" in str(exc.value)

    def test_missing_required_purpose_raises(self, minimal_system_dict: dict[str, Any]) -> None:
        del minimal_system_dict["purpose"]
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_missing_required_version_raises(self, minimal_system_dict: dict[str, Any]) -> None:
        del minimal_system_dict["version"]
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_missing_required_provider_raises(self, minimal_system_dict: dict[str, Any]) -> None:
        del minimal_system_dict["provider"]
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_missing_required_jurisdictions_raises(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        del minimal_system_dict["deployment_jurisdictions"]
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_missing_required_output_consumed_in_eu_raises(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        del minimal_system_dict["output_consumed_in_eu"]
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_empty_jurisdictions_list_rejected(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        minimal_system_dict["deployment_jurisdictions"] = []
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_deployer_optional(self, minimal_system_dict: dict[str, Any]) -> None:
        del minimal_system_dict["deployer"]
        system = SystemDescription(**minimal_system_dict)
        assert system.deployer is None

    def test_mitigations_default_empty_list(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        del minimal_system_dict["mitigations"]
        system = SystemDescription(**minimal_system_dict)
        assert system.mitigations == []

    def test_metadata_default_empty(self, minimal_system_dict: dict[str, Any]) -> None:
        del minimal_system_dict["metadata"]
        system = SystemDescription(**minimal_system_dict)
        assert system.metadata.owner is None

    def test_unknown_top_level_field_rejected(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        minimal_system_dict["sneaky_extra"] = "oops"
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_roundtrip_json_preserves_shape(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        original = SystemDescription(**minimal_system_dict)
        as_json = original.model_dump_json()
        reparsed = SystemDescription.model_validate_json(as_json)
        assert reparsed == original

    def test_jurisdiction_accepts_multiple(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        minimal_system_dict["deployment_jurisdictions"] = ["EU", "US", "UK"]
        system = SystemDescription(**minimal_system_dict)
        assert len(system.deployment_jurisdictions) == 3

    def test_purpose_cannot_be_empty_string(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        minimal_system_dict["purpose"] = ""
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)

    def test_system_description_cannot_be_empty(
        self, minimal_system_dict: dict[str, Any]
    ) -> None:
        minimal_system_dict["system_description"] = ""
        with pytest.raises(ValidationError):
            SystemDescription(**minimal_system_dict)
