"""Input models for LitmusAI screening — PRD §7.1."""

from __future__ import annotations

import re
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

_POPULATION_CATEGORIES = frozenset({
    "general_public",
    "minors",
    "workers",
    "students",
    "persons_with_disabilities",
    "persons_in_vulnerable_economic_situations",
    "other",
})


class SubjectPopulation(BaseModel, extra="forbid"):
    categories: list[str] = Field(..., min_length=1)
    notes: Optional[str] = None

    @field_validator("categories")
    @classmethod
    def _validate_categories(cls, v: list[str]) -> list[str]:
        for cat in v:
            if cat not in _POPULATION_CATEGORIES:
                msg = (
                    f"Unknown population category: {cat!r}. "
                    f"Allowed: {sorted(_POPULATION_CATEGORIES)}"
                )
                raise ValueError(msg)
        return v


class SystemInputs(BaseModel, extra="forbid"):
    biometric: bool = False
    facial_images: bool = False
    emotional_state_inference: bool = False
    behaviour_history: bool = False
    scraped_internet_data: bool = False
    freetext_prompts: bool = False
    other: Optional[str] = None


class SystemOutputs(BaseModel, extra="forbid"):
    individual_scores: bool = False
    behaviour_predictions: bool = False
    criminal_risk_predictions: bool = False
    emotion_inferences: bool = False
    sensitive_attribute_classifications: bool = False
    freetext_generations: bool = False
    other: Optional[str] = None


class DeploymentContext(BaseModel, extra="forbid"):
    workplace: bool = False
    education: bool = False
    public_space: bool = False
    real_time_operation: bool = False
    law_enforcement_use: bool = False
    healthcare: bool = False
    financial_services: bool = False
    other: Optional[str] = None


class Metadata(BaseModel, extra="forbid"):
    last_reviewed: Optional[date] = None
    owner: Optional[str] = None
    reviewed_by: Optional[str] = None


class SystemDescription(BaseModel, extra="forbid"):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    deployer: Optional[str] = None
    purpose: str = Field(..., min_length=1)
    system_description: str = Field(..., min_length=1)
    deployment_jurisdictions: list[str] = Field(..., min_length=1)
    output_consumed_in_eu: bool
    subject_population: SubjectPopulation
    inputs: SystemInputs = SystemInputs()
    outputs: SystemOutputs = SystemOutputs()
    deployment_context: DeploymentContext = DeploymentContext()
    mitigations: list[str] = Field(default_factory=list)
    metadata: Metadata = Metadata()
