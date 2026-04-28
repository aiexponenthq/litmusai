"""`litmus diff-ruleset <old> <new>` — PRD FR-26.

Compares two ruleset JSON files and renders the structural diff. Default
output is a Rich console table optimised for human review; `--format json`
emits the `RulesetDiff` model verbatim for CI pipelines.

Exit codes:
    0  rulesets are identical
    1  differences found (use this in CI to gate ruleset changes)
    2  invalid input file (missing or malformed)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from litmusai.cli.main import app
from litmusai.engine.diff import RulesetDiff, diff_rulesets
from litmusai.models.ruleset import Ruleset

console = Console()


def _load_ruleset(path: Path, label: str) -> Ruleset:
    """Load + validate a ruleset JSON file. Exits 2 on any failure."""
    if not path.exists():
        typer.echo(f"{label} file not found: {path}", err=True)
        raise typer.Exit(code=2)
    try:
        data = json.loads(path.read_text())
        return Ruleset.model_validate(data)
    except Exception as exc:
        typer.echo(f"Invalid {label} ruleset at {path}: {exc}", err=True)
        raise typer.Exit(code=2) from exc


def _truncate(value: object, limit: int = 60) -> str:
    text = str(value) if value is not None else "—"
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


def _render_human(diff: RulesetDiff) -> None:
    """Rich console rendering of a `RulesetDiff`."""
    header = (
        f"[bold]Ruleset diff[/bold]\n"
        f"  old: {diff.old_ruleset_version}\n"
        f"  new: {diff.new_ruleset_version}"
    )
    console.print(Panel(header, expand=False))

    summary = Table(show_header=True, header_style="bold", title="Summary")
    summary.add_column("Section")
    summary.add_column("Count", justify="right")
    summary.add_row("Added rules", str(len(diff.added_rules)))
    summary.add_row("Removed rules", str(len(diff.removed_rules)))
    summary.add_row("Modified rules", str(len(diff.modified_rules)))
    summary.add_row("Unchanged rules", str(diff.unchanged_rule_count))
    summary.add_row("Metadata changes", str(len(diff.metadata_changes)))
    console.print(summary)

    if diff.metadata_changes:
        meta_table = Table(show_header=True, header_style="bold", title="Metadata changes")
        meta_table.add_column("Field")
        meta_table.add_column("Old")
        meta_table.add_column("New")
        for change in diff.metadata_changes:
            meta_table.add_row(change.field, _truncate(change.old), _truncate(change.new))
        console.print(meta_table)

    if diff.added_rules:
        added_table = Table(show_header=True, header_style="bold", title="Added rules")
        added_table.add_column("Rule ID")
        added_table.add_column("Category")
        added_table.add_column("Verdict")
        added_table.add_column("Description")
        for rule in diff.added_rules:
            added_table.add_row(
                rule.id,
                rule.category,
                rule.verdict_if_triggered,
                _truncate(rule.description, 80),
            )
        console.print(added_table)

    if diff.removed_rules:
        removed_table = Table(show_header=True, header_style="bold", title="Removed rules")
        removed_table.add_column("Rule ID")
        removed_table.add_column("Category")
        removed_table.add_column("Verdict")
        removed_table.add_column("Description")
        for rule in diff.removed_rules:
            removed_table.add_row(
                rule.id,
                rule.category,
                rule.verdict_if_triggered,
                _truncate(rule.description, 80),
            )
        console.print(removed_table)

    if diff.modified_rules:
        for mod in diff.modified_rules:
            mod_table = Table(
                show_header=True,
                header_style="bold",
                title=f"Modified rule: {mod.id} ({mod.category})",
            )
            mod_table.add_column("Field")
            mod_table.add_column("Old")
            mod_table.add_column("New")
            for field_change in mod.changes:
                mod_table.add_row(
                    field_change.field,
                    _truncate(field_change.old),
                    _truncate(field_change.new),
                )
            console.print(mod_table)

    if not diff.has_changes:
        console.print("[green]No differences — rulesets are identical.[/green]")
    else:
        console.print(
            f"\n[bold]{diff.rule_change_total}[/bold] rule change(s) "
            f"+ {len(diff.metadata_changes)} metadata change(s).",
        )


@app.command(name="diff-ruleset")
def diff_ruleset_cmd(
    old: Path = typer.Argument(
        ...,
        help="Path to the older ruleset JSON file.",
        exists=False,
    ),
    new: Path = typer.Argument(
        ...,
        help="Path to the newer ruleset JSON file.",
        exists=False,
    ),
    output_format: str = typer.Option(
        "human",
        "--format",
        "-f",
        help="Output format: 'human' (rich console table) or 'json'.",
    ),
) -> None:
    """Compare two ruleset JSON files and report structural changes (FR-26)."""
    fmt: Literal["human", "json"]
    if output_format not in ("human", "json"):
        typer.echo(
            f"Invalid --format: {output_format!r}. Must be 'human' or 'json'.",
            err=True,
        )
        raise typer.Exit(code=2)
    fmt = output_format  # type: ignore[assignment]

    old_ruleset = _load_ruleset(old, "old")
    new_ruleset = _load_ruleset(new, "new")
    diff = diff_rulesets(old_ruleset, new_ruleset)

    if fmt == "json":
        typer.echo(diff.model_dump_json(indent=2))
    else:
        _render_human(diff)

    raise typer.Exit(code=1 if diff.has_changes else 0)
