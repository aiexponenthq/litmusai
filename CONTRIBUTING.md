# Contributing to LitmusAI

Thank you for considering contributing to LitmusAI. This project is maintained by [AiExponent LLC](https://aiexponent.com).

## How to Contribute

### Bug Reports

Open a GitHub issue with:
- LitmusAI version (`litmus --version`)
- Python version
- OS
- Steps to reproduce
- Expected vs actual behaviour

### Code Contributions

1. Fork the repo and create a feature branch from `main`.
2. Set up the dev environment: `pip install -e ".[dev]"`
3. Write tests first (TDD). Run: `pytest tests/ -v`
4. Ensure lint passes: `ruff check src/ tests/ && mypy --strict src/`
5. Open a PR against `main`.

### Ruleset Contributions

**Reference ruleset changes** (the default `aiexponent-reference-v1.0` ruleset) require internal panel approval and are not accepted via drive-by PRs. If you believe a rule is incorrect, open an issue with the regulatory citation and your proposed change.

**BYO rulesets** are encouraged. See `docs/ruleset-authoring.md` for the schema and signing format. We welcome community-authored signed rulesets as separate files.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
