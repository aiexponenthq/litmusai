"""LitmusAI CLI entry point — all commands registered here."""

from __future__ import annotations

import typer

from litmusai import __version__

app = typer.Typer(
    name="litmus",
    help="LitmusAI — Article 5 Prohibited AI Practice Screener.",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
)


def _version_callback(value: bool) -> None:
    """Multi-line version output — package version + ruleset legal status (FR-10).

    The `ruleset_legal_status` line is required by the G6 ruling: package
    SemVer reflects API stability; legal-review status rides on a content
    identifier on every distribution surface, including this output.
    """
    if value:
        import json
        from pathlib import Path

        from litmusai.models.ruleset import Ruleset

        # Active ruleset path: user-configured (litmus use-ruleset) or default
        active_config = Path.home() / ".config" / "litmusai" / "active-ruleset.json"
        bundled_default = (
            Path(__file__).resolve().parents[1]
            / "_data"
            / "ruleset"
            / "ruleset-2024-1689-v1.0.json"
        )
        ruleset_path = bundled_default
        if active_config.exists():
            try:
                cfg = json.loads(active_config.read_text())
                candidate = Path(cfg.get("path", ""))
                if candidate.exists():
                    ruleset_path = candidate
            except (json.JSONDecodeError, OSError):
                # Malformed or unreadable user config — fall through to bundled default.
                ruleset_path = bundled_default

        try:
            ruleset = Ruleset.model_validate(json.loads(ruleset_path.read_text()))
        except (json.JSONDecodeError, OSError, ValueError):
            # Never let a broken ruleset block --version output.
            typer.echo(
                f"litmusai {__version__}\n"
                f"ruleset_version: (unable to load active ruleset)\n"
                f"ruleset_legal_status: UNKNOWN",
            )
            raise typer.Exit() from None

        legal_status = "REVIEWED" if ruleset.signature is not None else "UNREVIEWED"
        signer_line = (
            f"\nruleset_signer: {ruleset.signature.signer_name}"
            if ruleset.signature is not None
            else ""
        )
        typer.echo(
            f"litmusai {__version__}\n"
            f"ruleset_version: {ruleset.ruleset_version}\n"
            f"ruleset_legal_status: {legal_status}"
            f"{signer_line}",
        )
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """LitmusAI — free, deterministic Article 5 screener.

    Not legal advice. Not a notified body.
    """


# Register commands — imported after app is defined to avoid circular imports.
import litmusai.cli.commands.debug as _debug  # noqa: F401, E402
import litmusai.cli.commands.diff_ruleset as _diff_ruleset  # noqa: F401, E402
import litmusai.cli.commands.export as _export  # noqa: F401, E402
import litmusai.cli.commands.init as _init  # noqa: F401, E402
import litmusai.cli.commands.portfolio as _portfolio  # noqa: F401, E402
import litmusai.cli.commands.ruleset_mgmt as _ruleset_mgmt  # noqa: F401, E402
import litmusai.cli.commands.screen as _screen  # noqa: F401, E402
import litmusai.cli.commands.verify as _verify  # noqa: F401, E402
