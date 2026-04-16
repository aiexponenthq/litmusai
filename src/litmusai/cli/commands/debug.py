"""litmus debug — print the rule-firing trace for a report (FR-33)."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from litmusai.cli.main import app

console = Console()


@app.command()
def debug(
    report_path: Path = typer.Argument(..., help="Path to a LitmusAI JSON report."),
) -> None:
    """Print the full rule-firing trace for a screening report."""
    try:
        data = json.loads(report_path.read_text())
    except Exception as exc:
        typer.echo(f"Error reading report: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    console.print(f"[bold]System:[/bold] {data.get('system', {}).get('name', 'unknown')}")
    console.print(f"[bold]Ruleset:[/bold] {data.get('ruleset_version', 'unknown')}")
    console.print(f"[bold]Overall:[/bold] {data.get('summary', {}).get('overall_verdict', '?')}")
    console.print()

    for cat_id, cat in data.get("categories", {}).items():
        verdict = cat.get("verdict", "?")
        style = {"red": "bold red", "amber": "yellow", "clear": "green"}.get(verdict, "")
        console.print(f"[{style}]{cat_id} — {cat.get('label', '')} → {verdict.upper()}[/{style}]")
        if cat.get("triggered_rules"):
            for rule_id in cat["triggered_rules"]:
                console.print(f"  [dim]triggered:[/dim] {rule_id}")
        console.print(f"  [dim]rationale:[/dim] {cat.get('rationale', '')}")
        console.print()
