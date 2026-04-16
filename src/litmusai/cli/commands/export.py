"""litmus export — export a screening report to different formats (FR-5, US-05)."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from litmusai.cli.main import app


@app.command(name="export")
def export_cmd(
    report_path: Path = typer.Argument(..., help="Path to a LitmusAI JSON report."),
    output: Path = typer.Option(..., "--output", "-o", help="Output file path."),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json, markdown, sarif.",
    ),
) -> None:
    """Export a screening report to JSON, Markdown, or SARIF."""
    try:
        report_data = json.loads(report_path.read_text())
    except Exception as exc:
        typer.echo(f"Error reading report: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    if fmt == "json":
        output.write_text(json.dumps(report_data, indent=2) + "\n")
    elif fmt == "markdown":
        from litmusai.export.markdown_exporter import to_markdown

        output.write_text(to_markdown(report_data))
    elif fmt == "sarif":
        from litmusai.export.sarif_exporter import to_sarif

        output.write_text(json.dumps(to_sarif(report_data), indent=2) + "\n")
    else:
        typer.echo(f"Unknown format: {fmt}. Use json, markdown, or sarif.", err=True)
        raise typer.Exit(code=2)

    typer.echo(f"Exported to {output} ({fmt})")
