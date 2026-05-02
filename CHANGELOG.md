# Changelog

All notable changes to LitmusAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-04-28

> **LitmusAI 1.0.0 ships with the AiExponent reference ruleset (UNREVIEWED — internal panel authored, no external lawyer review). Apache 2.0, AS IS.**
>
> Package SemVer reflects API stability. The CLI surface, JSON / SARIF schema, and BYO-ruleset contract are stable for production integration. The `ruleset_legal_status: UNREVIEWED` line printed by `litmus version` separates the legal-review status from the package version — a future `ruleset-2024-1689-v1.1` release will land `legal_status: REVIEWED` once external lawyer review completes.

### Added — engine

- **Eight-category Article 5 screening engine.** Pure-Python, deterministic, all `system.*` field accesses go through a constrained expression language with no `eval` and no Python execution. 22 reference rules covering all eight Article 5 sub-points (5.1.a–h).
- **Conservative-by-default verdict logic.** Where the regulatory text is ambiguous, the ruleset prefers `amber` over `clear` so a qualified reviewer takes the final call.
- **Per-rule confidence band** (`high` / `medium` / `low`) on every verdict so reviewers can prioritise the soft calls.
- **SHA-256 input hash** on every report (`canonical_json` via RFC 8785 ordering, with `date` / `datetime` coercion to ISO strings).
- **Override mechanism** with full audit trail (`OverrideEntry`) — FR-10.

### Added — CLI commands

- `litmus screen [path|--describe]` — primary screening surface, rich console + multiple formats
- `litmus init` — scaffold a starter `system.yaml` (FR-7)
- `litmus export <report> --format {json|markdown|sarif|pdf}` — converters; PDF via optional WeasyPrint extra
- `litmus debug <report>` — full rule-firing trace per category (FR-33)
- `litmus verify <report>` — re-hash the input and confirm the report has not been tampered with
- `litmus portfolio <dir>` — bulk-screen every `system.yaml` in a directory
- `litmus use-ruleset <path>` — set a custom (BYO) ruleset as active (FR-34)
- `litmus verify-ruleset <path>` — validate a ruleset's structure + optional signature (FR-35)
- `litmus ruleset-info` — print provenance of the currently-active ruleset (FR-36)
- `litmus diff-ruleset <old> <new>` — structural diff between two rulesets, with `--format json` for CI (FR-26)
- `litmus --version` — multi-line: package version + ruleset version + ruleset legal status + signer

### Added — exporters

- **SARIF 2.1.0** output mapping each Article 5 sub-point to a SARIF rule ID — compatible with GitHub Advanced Security, GitLab SAST, Azure DevOps Advanced Security (FR-29)
- **Markdown** export for human-readable governance reports
- **PDF** export via WeasyPrint (optional extra: `pip install litmusai[pdf]`)

### Added — BYO-ruleset

- Optional `RulesetSignature` block on every `Ruleset`. Supported algorithms: `sha256`, `pgp-detached`, `x509-pkcs7`.
- Provenance header on every report (FR-36): `(SIGNED by: <signer> · <date>)` for signed rulesets, `(UNREVIEWED — internal panel authored, no external legal review)` for the default
- `docs/ruleset-authoring.md` walks through the schema, the signing format, and a worked example using the dummy-signed `tests/fixtures/rulesets/acme-corp-signed-v1.0.json`

### Added — distribution surface (G6 mitigations)

- README first-section blockquote carries the verbatim UNREVIEWED disclosure (renders on PyPI's project page via `long_description`)
- New badge: `ruleset_legal_status: UNREVIEWED`, anchored to the in-README "Legal review status" section
- `litmus version` output adds `ruleset_legal_status: …` and `ruleset_signer: …` lines so the legal status surfaces at the command line, not just in reports
- Pre-drafted GitHub release-note body at `docs/release-notes-v1.0.0.md` — used by the release-on-tag workflow
- Release-note title format: `v1.0.0 — Article 5 screener (UNREVIEWED ruleset, internal panel authored)`

### Added — developer experience

- **GitHub Action wrapper** at `aiexponenthq/litmusai/.github/actions/litmusai-screen@v1` — drop-in CI integration with `path`, `fail-on`, `output-format`, and `override-file` inputs (FR-27)
- **Conventional exit codes** (FR-28): 0 = clear / below-threshold, 1 = threshold exceeded, 2 = invalid input / schema error, 3 = tamper detected
- Three worked-example `system.yaml` files in `examples/` covering CLEAR (`example-clear.yaml`), AMBER (`example-amber.yaml`), and RED (`example-red.yaml`) verdicts. CI pin via `tests/integration/test_examples.py` ensures any future ruleset change that flips an example's verdict surfaces before release.

### Added — quality gates

- **257 tests passing** under `pytest --disable-socket` (NFR-8 zero-network gate)
- **87.39% coverage** across engine + models (PRD target: ≥ 80%)
- **`mypy --strict`** clean across 26 source files
- **`ruff check`** + **`ruff format --check`** clean across 45 files
- **`licensecheck`** clean — all 22 production dependencies are Apache / MIT / BSD compatible
- CI matrix: Ubuntu / macOS / Windows × Python 3.11 / 3.12 / 3.13

### Notes

- **Legal-review status: UNREVIEWED.** External lawyer review is **not** a release blocker per the project's published acceptance criteria (PRD §NFR-10). The package ships with conservative-by-default verdicts, prominent `UNREVIEWED` disclaimers on every distribution surface, and a Bring-Your-Own-Ruleset mechanism so customers with their own counsel can supply a signed ruleset today. A future `ruleset-2024-1689-v1.1` release will bump the ruleset's `legal_status` to `REVIEWED`; the LitmusAI package version (`1.0.x`) tracks API stability and will not bump for that change.
- **Not legal advice. Not a notified body.** Apache 2.0. AS IS.
