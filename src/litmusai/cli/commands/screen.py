"""litmus screen — run Article 5 screening (FR-1 to FR-19, US-01, US-20)."""

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
from litmusai.models.system import (
    DeploymentContext,
    SubjectPopulation,
    SystemDescription,
    SystemInputs,
    SystemOutputs,
)

console = Console()

_DEFAULT_RULESET = (
    Path(__file__).resolve().parents[2] / "_data" / "ruleset" / "ruleset-2024-1689-v1.0.json"
)

_VERDICT_STYLE = {
    "clear": "[green]CLEAR[/green]",
    "amber": "[yellow]AMBER[/yellow]",
    "red": "[bold red]RED[/bold red]",
}


def _load_ruleset(path: Path | None = None) -> Ruleset:
    p = path or _DEFAULT_RULESET
    return Ruleset.model_validate(json.loads(p.read_text()))


def _quickscreen_to_system(describe: str) -> SystemDescription:
    """Build a SystemDescription from free text via keyword inference.

    This is the Steve Jobs critical path — a PM should be able to run
    `litmus screen --describe "a chatbot for mental health support for teenagers"`
    and get a meaningful verdict in 20 seconds without knowing YAML.
    """
    text = describe.lower()

    # Population inference
    populations: list[str] = ["general_public"]
    if any(w in text for w in ("teenager", "teens", "child", "children", "minor", "youth", "kid")):
        populations = ["minors"]
    if (
        any(
            w in text
            for w in ("elderly", "disabled", "disability", "vulnerable", "low-income", "poverty")
        )
        and "persons_in_vulnerable_economic_situations" not in populations
    ):
        populations.append("persons_in_vulnerable_economic_situations")
    if (
        any(w in text for w in ("worker", "employee", "staff", "workplace"))
        and "workers" not in populations
    ):
        populations.append("workers")
    if (
        any(w in text for w in ("student", "school", "university", "classroom"))
        and "students" not in populations
    ):
        populations.append("students")

    # Input inference
    biometric = any(w in text for w in ("biometric", "fingerprint", "iris", "face scan"))
    facial = any(w in text for w in ("facial", "face recognition", "face detection", "face image"))
    emotion_input = any(w in text for w in ("emotion", "sentiment", "mood", "feeling", "affect"))
    behaviour = any(w in text for w in ("behaviour", "behavior", "engagement", "habit", "pattern"))
    scraped = any(w in text for w in ("scrape", "scraped", "crawl", "internet data", "web data"))
    freetext = any(
        w in text for w in ("chatbot", "chat", "prompt", "conversational", "generate text")
    )

    # Output inference
    scores = any(w in text for w in ("score", "scoring", "rating", "rank", "grade"))
    behaviour_pred = any(
        w in text
        for w in ("predict behaviour", "predict behavior", "engagement predict", "feed ranking")
    )
    criminal = any(w in text for w in ("criminal", "recidivism", "offend", "crime predict"))
    emotion_out = emotion_input
    sensitive = any(
        w in text for w in ("race", "ethnicity", "religion", "sexual orientation", "gender classif")
    )
    freetext_out = freetext

    # Context inference
    workplace = any(w in text for w in ("workplace", "office", "employee", "hr ", "human resource"))
    education = any(
        w in text for w in ("school", "education", "classroom", "university", "student")
    )
    public_space = any(
        w in text for w in ("public space", "street", "cctv", "surveillance", "public area")
    )
    realtime = any(w in text for w in ("real-time", "realtime", "live", "real time"))
    law_enforcement = any(w in text for w in ("police", "law enforcement", "security force"))
    healthcare = any(
        w in text for w in ("health", "medical", "clinical", "patient", "hospital", "icu")
    )
    financial = any(w in text for w in ("loan", "credit", "financial", "bank", "insurance"))

    return SystemDescription(
        name="Quick Screen",
        version="0.0.0",
        provider="Unknown",
        purpose=describe,
        system_description=describe,
        deployment_jurisdictions=["EU"],
        output_consumed_in_eu=True,
        subject_population=SubjectPopulation(categories=populations),
        inputs=SystemInputs(
            biometric=biometric,
            facial_images=facial,
            emotional_state_inference=emotion_input,
            behaviour_history=behaviour,
            scraped_internet_data=scraped,
            freetext_prompts=freetext,
        ),
        outputs=SystemOutputs(
            individual_scores=scores,
            behaviour_predictions=behaviour_pred,
            criminal_risk_predictions=criminal,
            emotion_inferences=emotion_out,
            sensitive_attribute_classifications=sensitive,
            freetext_generations=freetext_out,
        ),
        deployment_context=DeploymentContext(
            workplace=workplace,
            education=education,
            public_space=public_space,
            real_time_operation=realtime,
            law_enforcement_use=law_enforcement,
            healthcare=healthcare,
            financial_services=financial,
        ),
    )


def _print_summary(report_data: dict) -> None:  # type: ignore[type-arg]
    summary = report_data["summary"]
    prov = report_data["ruleset_provenance"]

    console.print()
    console.print(f"[bold]Ruleset:[/bold] {prov['display_label']}")
    console.print(f"[bold]Input hash:[/bold] {report_data['input_hash_sha256'][:16]}...")
    console.print()

    table = Table(title="Article 5 Screening Results", show_lines=True)
    table.add_column("Category", style="bold")
    table.add_column("Verdict", justify="center")
    table.add_column("Confidence", justify="center")
    table.add_column("Rules Triggered")

    for cat_id, cat in report_data["categories"].items():
        verdict_str = _VERDICT_STYLE.get(cat["verdict"], cat["verdict"])
        rules = ", ".join(cat["triggered_rules"]) if cat["triggered_rules"] else "-"
        table.add_row(
            f"{cat_id} {cat['label']}",
            verdict_str,
            cat["confidence"],
            rules,
        )

    console.print(table)
    console.print()

    overall_style = _VERDICT_STYLE.get(summary["overall_verdict"], summary["overall_verdict"])
    console.print(f"[bold]Overall verdict:[/bold] {overall_style}")
    console.print(
        f"  Red: {summary['red_count']} · Amber: {summary['amber_count']} · "
        f"Clear: {summary['clear_count']}"
    )
    if summary["requires_legal_review"]:
        console.print("[bold yellow]Requires legal review before deployment.[/bold yellow]")
    console.print()
    console.print("[dim]Not legal advice. Not a notified body.[/dim]")


@app.command()
def screen(
    path: Path = typer.Argument(None, help="Path to system.yaml."),
    describe: str = typer.Option(
        None,
        "--describe",
        "-d",
        help="Quick screen from free text (no YAML needed).",
    ),
    output: Path = typer.Option(None, "--output", "-o", help="Write JSON report to file."),
    fail_on: str = typer.Option(
        "red",
        "--fail-on",
        help="Exit non-zero on this verdict or worse. Options: red, amber, none.",
    ),
    ruleset_path: Path = typer.Option(None, "--ruleset", help="Path to custom ruleset JSON."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress table output."),
) -> None:
    """Screen an AI system against Article 5 of the EU AI Act."""
    if path is None and describe is None:  # type: ignore[unreachable]
        typer.echo("Provide a system.yaml path or use --describe for quick screen.", err=True)  # type: ignore[unreachable]
        raise typer.Exit(code=2)

    ruleset = _load_ruleset(ruleset_path)
    screener = Screener(ruleset)

    if describe:
        system = _quickscreen_to_system(describe)
    else:
        assert path is not None
        try:
            raw = yaml.safe_load(path.read_text())
        except Exception as exc:
            typer.echo(f"Error reading {path}: {exc}", err=True)
            raise typer.Exit(code=2) from exc

        try:
            system = SystemDescription.model_validate(raw)
        except ValidationError as exc:
            typer.echo(f"Schema validation error:\n{exc}", err=True)
            raise typer.Exit(code=2) from exc

    report = screener.screen(system)
    report_data = json.loads(report.model_dump_json())

    if output:
        output.write_text(json.dumps(report_data, indent=2) + "\n")
        if not quiet:
            typer.echo(f"Report written to {output}")

    if not quiet:
        _print_summary(report_data)

    verdict = report.summary.overall_verdict
    if fail_on == "red" and verdict == "red":
        raise typer.Exit(code=1)
    if fail_on == "amber" and verdict in ("red", "amber"):
        raise typer.Exit(code=1)
