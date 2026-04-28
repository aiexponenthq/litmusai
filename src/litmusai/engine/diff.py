"""Ruleset diff engine — PRD FR-26.

Compares two `Ruleset` instances rule-by-rule and surfaces structural
changes: added rules, removed rules, modified rules (with field-level
detail), plus changes to top-level metadata (ruleset_version, regulation,
effective_date, signature presence + signer identity).

Pure, deterministic, no I/O. The CLI wrapper at
`litmusai.cli.commands.diff_ruleset` reads files from disk and renders
the result; this module operates on already-loaded `Ruleset` instances.

The output `RulesetDiff` Pydantic model is the same shape that the
future `ruleset-changelog.json` artifact (FR-26) will adopt in v1.1
when the first rule-content changes ship.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from litmusai.models.ruleset import Rule, Ruleset

# Fields on Rule that are content-bearing (changes here count as a real
# rule modification). Identity field `id` is matched on, not compared.
_RULE_CONTENT_FIELDS: tuple[str, ...] = (
    "category",
    "version",
    "description",
    "expression",
    "verdict_if_triggered",
    "confidence_delta",
    "citations",
    "reviewed_by",
    "reviewed_date",
)


class RuleFieldChange(BaseModel, extra="forbid"):
    """A single field change inside a modified rule."""

    field: str
    old: Any = None
    new: Any = None


class RuleModification(BaseModel, extra="forbid"):
    """A rule that exists on both sides but with different content."""

    id: str
    category: str
    changes: list[RuleFieldChange] = Field(default_factory=list)


class MetadataChange(BaseModel, extra="forbid"):
    """A change to a top-level ruleset metadata field."""

    field: str
    old: Any = None
    new: Any = None


class RulesetDiff(BaseModel, extra="forbid"):
    """Structured diff between two rulesets.

    Stable JSON shape — the CLI's `--format json` and the future
    `ruleset-changelog.json` artifact both serialize from this model.
    """

    old_ruleset_version: str
    new_ruleset_version: str
    added_rules: list[Rule] = Field(default_factory=list)
    removed_rules: list[Rule] = Field(default_factory=list)
    modified_rules: list[RuleModification] = Field(default_factory=list)
    unchanged_rule_count: int = 0
    metadata_changes: list[MetadataChange] = Field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """True if anything differs between the two rulesets."""
        return bool(
            self.added_rules or self.removed_rules or self.modified_rules or self.metadata_changes
        )

    @property
    def rule_change_total(self) -> int:
        """Total count of added + removed + modified rules."""
        return len(self.added_rules) + len(self.removed_rules) + len(self.modified_rules)


def _compare_rules(old_rule: Rule, new_rule: Rule) -> list[RuleFieldChange]:
    """Per-field comparison of two rules with the same ID."""
    changes: list[RuleFieldChange] = []
    for field in _RULE_CONTENT_FIELDS:
        old_value = getattr(old_rule, field)
        new_value = getattr(new_rule, field)
        if old_value != new_value:
            changes.append(RuleFieldChange(field=field, old=old_value, new=new_value))
    return changes


def _compare_metadata(old: Ruleset, new: Ruleset) -> list[MetadataChange]:
    """Top-level metadata diff: regulation, effective_date, signature."""
    changes: list[MetadataChange] = []
    if old.regulation != new.regulation:
        changes.append(MetadataChange(field="regulation", old=old.regulation, new=new.regulation))
    if old.effective_date != new.effective_date:
        changes.append(
            MetadataChange(field="effective_date", old=old.effective_date, new=new.effective_date),
        )
    # Signature presence transition is the most important regulatory signal.
    old_sig_status = "signed" if old.signature else "unsigned"
    new_sig_status = "signed" if new.signature else "unsigned"
    if old_sig_status != new_sig_status:
        changes.append(
            MetadataChange(field="signature_status", old=old_sig_status, new=new_sig_status),
        )
    elif old.signature and new.signature and old.signature.signer_name != new.signature.signer_name:
        changes.append(
            MetadataChange(
                field="signature_signer",
                old=old.signature.signer_name,
                new=new.signature.signer_name,
            ),
        )
    return changes


def diff_rulesets(old: Ruleset, new: Ruleset) -> RulesetDiff:
    """Produce a structured diff of two rulesets.

    Identity is matched on `Rule.id`. A rule with the same ID on both
    sides but different content is reported as `modified`; a rule on
    only one side is reported as added/removed.
    """
    old_by_id = {r.id: r for r in old.rules}
    new_by_id = {r.id: r for r in new.rules}

    old_ids = set(old_by_id)
    new_ids = set(new_by_id)

    added = [new_by_id[i] for i in sorted(new_ids - old_ids)]
    removed = [old_by_id[i] for i in sorted(old_ids - new_ids)]

    modified: list[RuleModification] = []
    unchanged = 0
    for rid in sorted(old_ids & new_ids):
        field_changes = _compare_rules(old_by_id[rid], new_by_id[rid])
        if field_changes:
            modified.append(
                RuleModification(
                    id=rid,
                    category=new_by_id[rid].category,
                    changes=field_changes,
                ),
            )
        else:
            unchanged += 1

    return RulesetDiff(
        old_ruleset_version=old.ruleset_version,
        new_ruleset_version=new.ruleset_version,
        added_rules=added,
        removed_rules=removed,
        modified_rules=modified,
        unchanged_rule_count=unchanged,
        metadata_changes=_compare_metadata(old, new),
    )
