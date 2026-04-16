"""litmus init — create a starter system.yaml template (FR-3, US-13)."""

from __future__ import annotations

from pathlib import Path

import typer

from litmusai.cli.main import app

_TEMPLATE = """\
# LitmusAI System Description
# Edit the fields below to describe your AI system.
# Then run: litmus screen system.yaml

name: "My AI System"
version: "1.0.0"
provider: "My Organisation"
deployer: "My Organisation"
purpose: "Describe what the system does in one sentence."
system_description: |
  A more detailed description of the system: what inputs it takes,
  what outputs it produces, and how those outputs are used.

deployment_jurisdictions:
  - EU

output_consumed_in_eu: true

subject_population:
  categories:
    - general_public
  notes: null

inputs:
  biometric: false
  facial_images: false
  emotional_state_inference: false
  behaviour_history: false
  scraped_internet_data: false
  freetext_prompts: false
  other: null

outputs:
  individual_scores: false
  behaviour_predictions: false
  criminal_risk_predictions: false
  emotion_inferences: false
  sensitive_attribute_classifications: false
  freetext_generations: false
  other: null

deployment_context:
  workplace: false
  education: false
  public_space: false
  real_time_operation: false
  law_enforcement_use: false
  healthcare: false
  financial_services: false
  other: null

mitigations: []

metadata:
  last_reviewed: null
  owner: null
  reviewed_by: null
"""


@app.command()
def init(
    output: Path = typer.Option(
        Path("system.yaml"),
        "--output",
        "-o",
        help="Path for the generated system description file.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if file exists."),
) -> None:
    """Create a starter system.yaml template."""
    if output.exists() and not force:
        typer.echo(f"File already exists: {output}. Use --force to overwrite.", err=True)
        raise typer.Exit(code=2)

    output.write_text(_TEMPLATE)
    typer.echo(f"Created {output}. Edit it, then run: litmus screen {output}")
