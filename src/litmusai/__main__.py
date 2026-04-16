"""Allow `python -m litmusai` as an alias for the `litmus` CLI."""

from litmusai.cli.main import app

if __name__ == "__main__":  # pragma: no cover
    app()
