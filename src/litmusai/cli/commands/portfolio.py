"""litmus portfolio — batch screening of multiple system.yaml files (FR-7, US-06)."""

from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from litmusai.cli.main import app
from litmusai.engine.screener import Screener
from litmusai.models.ruleset import Ruleset
from litmusai.models.system import SystemDescription

console = Console()

_DEFAULT_RULESET = (
    Path(__file__).resolve().parents[2] / "_data" / "ruleset" / "ruleset-2024-1689-v1.0.json"
)


@app.command()
def portfolio(
    directory: Path = typer.Argument(..., help="Directory containing system.yaml files."),
    output: Path = typer.Option(None, "--output", "-o", help="Write portfolio JSON report."),
    ruleset_path: Path = typer.Option(None, "--ruleset", help="Path to custom ruleset JSON."),
) -> None:
    """Screen all system.yaml files in a directory."""
    rs_path = ruleset_path or _DEFAULT_RULESET
    ruleset = Ruleset.model_validate(json.loads(rs_path.read_text()))
    screener = Screener(ruleset)

    yaml_files = sorted(directory.glob("*.yaml")) + sorted(directory.glob("*.yml"))
    if not yaml_files:
        typer.echo(f"No .yaml/.yml files found in {directory}", err=True)
        raise typer.Exit(code=2)

    results = []
    table = Table(title="Portfolio Screening", show_lines=True)
    table.add_column("File", style="bold")
    table.add_column("System", style="dim")
    table.add_column("Verdict", justify="center")
    table.add_column("Red", justify="center")
    table.add_column("Amber", justify="center")

    for yf in yaml_files:
        try:
            raw = yaml.safe_load(yf.read_text())
            system = SystemDescription.model_validate(raw)
            report = screener.screen(system)
            verdict = report.summary.overall_verdict
            style = {"red": "bold red", "amber": "yellow", "clear": "green"}.get(verdict, "")
            table.add_row(
                yf.name,
                system.name,
                f"[{style}]{verdict.upper()}[/{style}]",
                str(report.summary.red_count),
                str(report.summary.amber_count),
            )
            results.append(json.loads(report.model_dump_json()))
        except (ValidationError, Exception) as exc:
            table.add_row(yf.name, "ERROR", f"[red]{exc!s:.40}[/red]", "-", "-")

    console.print(table)

    if output:
        output.write_text(json.dumps(results, indent=2) + "\n")
        typer.echo(f"Portfolio report written to {output}")
