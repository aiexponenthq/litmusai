"""BYO-ruleset management commands — FR-34, FR-35, FR-36."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from litmusai.cli.main import app
from litmusai.models.ruleset import Ruleset

console = Console()

_CONFIG_DIR = Path.home() / ".config" / "litmusai"
_ACTIVE_RULESET_FILE = _CONFIG_DIR / "active-ruleset.json"


@app.command(name="use-ruleset")
def use_ruleset(
    path: Path = typer.Argument(..., help="Path to a custom ruleset JSON file."),
) -> None:
    """Set a custom ruleset as the active ruleset for subsequent screenings."""
    if not path.exists():
        typer.echo(f"File not found: {path}", err=True)
        raise typer.Exit(code=2)

    try:
        data = json.loads(path.read_text())
        ruleset = Ruleset.model_validate(data)
    except Exception as exc:
        typer.echo(f"Invalid ruleset: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _ACTIVE_RULESET_FILE.write_text(json.dumps({"path": str(path.resolve())}))

    sig = ruleset.signature
    if sig:
        console.print(f"[green]Active ruleset set:[/green] {ruleset.ruleset_version}")
        console.print(f"  Signed by: {sig.signer_name} ({sig.signed_date})")
    else:
        console.print(f"[yellow]Active ruleset set:[/yellow] {ruleset.ruleset_version}")
        console.print("  [dim]UNREVIEWED — no signature[/dim]")

    console.print(f"  Rules: {len(ruleset.rules)}")
    console.print(f"  Config saved to: {_ACTIVE_RULESET_FILE}")


@app.command(name="verify-ruleset")
def verify_ruleset(
    path: Path = typer.Argument(..., help="Path to a ruleset JSON file to verify."),
) -> None:
    """Verify a ruleset's structure and optional signature."""
    if not path.exists():
        typer.echo(f"File not found: {path}", err=True)
        raise typer.Exit(code=2)

    try:
        data = json.loads(path.read_text())
        ruleset = Ruleset.model_validate(data)
    except Exception as exc:
        typer.echo(f"Invalid ruleset schema: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    console.print(f"[green]Schema valid:[/green] {ruleset.ruleset_version}")
    console.print(f"  Regulation: {ruleset.regulation}")
    console.print(f"  Rules: {len(ruleset.rules)}")

    if ruleset.signature:
        console.print(f"  Signer: {ruleset.signature.signer_name}")
        console.print(f"  Algorithm: {ruleset.signature.signature_algorithm}")
        console.print(f"  Signed: {ruleset.signature.signed_date}")
        console.print(
            "  [yellow]Note: cryptographic signature verification is a v1.1 feature.[/yellow]"
        )
        console.print(
            "  Signature status: [green]PRESENT[/green] (schema valid, crypto check pending)"
        )
    else:
        console.print("  Signature: [dim]UNSIGNED[/dim]")

    raise typer.Exit(code=0)


@app.command(name="ruleset-info")
def ruleset_info(
    path: Path = typer.Argument(None, help="Path to a specific ruleset (or show active)."),
) -> None:
    """Show provenance of the active or specified ruleset."""
    if path is None:  # pragma: no branch — Typer makes this unreachable to mypy
        path = (  # type: ignore[unreachable]
            Path(__file__).resolve().parents[2]
            / "_data"
            / "ruleset"
            / "ruleset-2024-1689-v0.1.json"
        )

    if not path.exists():
        typer.echo(f"Ruleset not found: {path}", err=True)
        raise typer.Exit(code=2)

    try:
        data = json.loads(path.read_text())
        ruleset = Ruleset.model_validate(data)
    except Exception as exc:
        typer.echo(f"Error loading ruleset: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    console.print(f"[bold]Ruleset version:[/bold] {ruleset.ruleset_version}")
    console.print(f"[bold]Regulation:[/bold] {ruleset.regulation}")
    console.print(f"[bold]Effective date:[/bold] {ruleset.effective_date}")
    console.print(f"[bold]Total rules:[/bold] {len(ruleset.rules)}")

    categories: dict[str, list[str]] = {}
    for rule in ruleset.rules:
        categories.setdefault(rule.category, []).append(rule.id)
    for cat_id in sorted(categories):
        console.print(f"  {cat_id}: {len(categories[cat_id])} rules")

    if ruleset.signature:
        console.print(f"[bold]Signer:[/bold] {ruleset.signature.signer_name}")
        console.print(f"[bold]Signed:[/bold] {ruleset.signature.signed_date}")
        console.print("[bold]Status:[/bold] [green]SIGNED[/green]")
    else:
        console.print("[bold]Status:[/bold] [yellow]UNREVIEWED — internal panel authored[/yellow]")
