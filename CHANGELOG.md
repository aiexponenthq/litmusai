# Changelog

All notable changes to LitmusAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pydantic v2 data models: `SystemDescription`, `ScreeningReport`, `Ruleset`
- BYO-ruleset signature schema (`RulesetSignature`) per FR-34
- Ruleset provenance header (`RulesetProvenance`) per FR-36
- Typer CLI shell with `--version` and `--help`
- JSON Schema exports for all three models
- 82+ unit tests, boundary tests, CLI smoke tests
- CI workflow (lint, type check, test matrix, license check)
