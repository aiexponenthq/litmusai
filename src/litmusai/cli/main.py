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
    if value:
        typer.echo(f"litmusai {__version__}")
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
import litmusai.cli.commands.export as _export  # noqa: F401, E402
import litmusai.cli.commands.init as _init  # noqa: F401, E402
import litmusai.cli.commands.portfolio as _portfolio  # noqa: F401, E402
import litmusai.cli.commands.ruleset_mgmt as _ruleset_mgmt  # noqa: F401, E402
import litmusai.cli.commands.screen as _screen  # noqa: F401, E402
import litmusai.cli.commands.verify as _verify  # noqa: F401, E402
