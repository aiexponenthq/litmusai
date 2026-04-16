"""Ruleset models including optional BYO signature block — PRD §7.3, FR-23, FR-34."""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

_ARTICLE_5_CATEGORIES = frozenset({
    "5.1.a", "5.1.b", "5.1.c", "5.1.d",
    "5.1.e", "5.1.f", "5.1.g", "5.1.h",
})

_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")

Verdict = Literal["clear", "amber", "red"]
SignatureAlgorithm = Literal["sha256", "pgp-detached", "x509-pkcs7"]


class Rule(BaseModel, extra="forbid"):
    id: str
    category: str
    version: str
    description: str
    expression: str
    verdict_if_triggered: Verdict
    confidence_delta: Optional[int] = None
    citations: list[str] = Field(default_factory=list)
    reviewed_by: str
    reviewed_date: str

    @field_validator("id")
    @classmethod
    def _validate_id_snake_case(cls, v: str) -> str:
        if not _SNAKE_CASE_RE.fullmatch(v):
            msg = (
                f"Rule ID must be snake_case (lowercase letters, digits, underscores, "
                f"starting with a letter). Got: {v!r}"
            )
            raise ValueError(msg)
        return v

    @field_validator("category")
    @classmethod
    def _validate_category(cls, v: str) -> str:
        if v not in _ARTICLE_5_CATEGORIES:
            msg = f"Category must be one of {sorted(_ARTICLE_5_CATEGORIES)}. Got: {v!r}"
            raise ValueError(msg)
        return v


class RulesetSignature(BaseModel, extra="forbid"):
    signer_name: str = Field(..., min_length=1)
    signer_bar_number: Optional[str] = None
    signer_firm: Optional[str] = None
    signer_email: EmailStr
    signed_date: str
    signature_algorithm: SignatureAlgorithm
    signature_value: str = Field(..., min_length=1)


class Ruleset(BaseModel, extra="forbid"):
    ruleset_version: str
    regulation: str
    effective_date: str
    rules: list[Rule] = Field(..., min_length=1)
    signature: Optional[RulesetSignature] = None

    @model_validator(mode="after")
    def _validate_unique_rule_ids(self) -> "Ruleset":
        ids = [r.id for r in self.rules]
        if len(ids) != len(set(ids)):
            msg = "Rule IDs must be unique within a ruleset."
            raise ValueError(msg)
        return self
