"""LitmusAI — Article 5 Prohibited AI Practice Screener.

Free, deterministic, CLI screener for Article 5 of Regulation (EU) 2024/1689.

This package is Apache 2.0 licensed and ships with an UNREVIEWED reference
ruleset authored by the AiExponent internal compliance panel. See
`docs/ruleset-authoring.md` for the Bring-Your-Own-Ruleset path.
"""

from importlib.metadata import PackageNotFoundError, version

# The PyPI distribution name is `litmus-screener` (the brand is "LitmusAI";
# the distribution name differs because `litmus-ai` was already taken on
# PyPI by an unrelated project). The Python module stays `litmusai` and
# the CLI command stays `litmus`.
try:
    __version__ = version("litmus-screener")
except PackageNotFoundError:  # pragma: no cover — editable/dev install
    __version__ = "0.0.0+local"

__all__ = ["__version__"]
