"""Output models for LitmusAI screening reports — PRD §7.2, FR-36."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from litmusai.models.system import SystemDescription

Verdict = Literal["clear", "amber", "red"]
Confidence = Literal["high", "medium", "low"]
SignatureStatus = Literal["unsigned", "verified", "invalid"]


class Citation(BaseModel, extra="forbid"):
    article: str = Field(..., min_length=1)
    recital: Optional[str] = None


class CategoryResult(BaseModel, extra="forbid"):
    label: str
    verdict: Verdict
    confidence: Confidence
    rationale: str = Field(..., min_length=1)
    triggered_rules: list[str] = Field(default_factory=list)
    regulation_citations: list[Citation] = Field(default_factory=list)
    remediation: list[str] = Field(default_factory=list)


class ReportSummary(BaseModel, extra="forbid"):
    overall_verdict: Verdict
    red_count: int = Field(..., ge=0)
    amber_count: int = Field(..., ge=0)
    clear_count: int = Field(..., ge=0)
    requires_legal_review: bool
    highest_penalty_exposure: str


class RulesetProvenance(BaseModel, extra="forbid"):
    ruleset_version: str
    regulation: str
    effective_date: str
    signer_name: Optional[str] = None
    signed_date: Optional[str] = None
    signature_status: SignatureStatus
    display_label: str


class OverrideEntry(BaseModel, extra="forbid"):
    category: str
    verdict_before: Verdict
    verdict_after: Verdict
    rationale: str
    approver: str
    approver_email: EmailStr
    approved_at: datetime


class ScreeningReport(BaseModel, extra="forbid"):
    report_version: str = "1.0"
    ruleset_version: str
    litmusai_version: str
    generated_at: datetime
    input_hash_sha256: str = Field(..., min_length=64, max_length=64)
    system: SystemDescription
    categories: dict[str, CategoryResult]
    summary: ReportSummary
    ruleset_provenance: RulesetProvenance
    disclaimers: list[str] = Field(default_factory=list)
    overrides_applied: list[OverrideEntry] = Field(default_factory=list)

    @field_validator("input_hash_sha256")
    @classmethod
    def _validate_sha256(cls, v: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{64}", v):
            msg = "input_hash_sha256 must be exactly 64 hex characters."
            raise ValueError(msg)
        return v
