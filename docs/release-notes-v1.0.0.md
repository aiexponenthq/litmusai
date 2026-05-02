# LitmusAI v1.0.0 (UNREVIEWED — internal panel authored, no external lawyer review)

> **GitHub release title (verbatim):**
> `v1.0.0 — Article 5 screener (UNREVIEWED ruleset, internal panel authored)`

> **One-line summary for X / LinkedIn / HN:**
> Free, deterministic, offline EU AI Act Article 5 screener. CLI + Python library. Apache 2.0. UNREVIEWED reference ruleset (no external lawyer review yet); BYO signed ruleset supported via `litmus use-ruleset`.

---

## Highlights

- **All eight Article 5 prohibited-practice categories covered** with a 22-rule reference ruleset, conservative-by-default (Amber preferred over Clear on ambiguity)
- **Zero network calls** during screening — enforced in CI via `pytest-socket --disable-socket` (NFR-8)
- **Deterministic**: same input + same ruleset = same output, with a SHA-256 input hash on every report
- **BYO-ruleset** mechanism — ship your lawyer-signed ruleset and `litmus use-ruleset your.json`; reports show `(SIGNED by: …)` instead of `UNREVIEWED`
- **Multiple output formats**: rich console table, JSON, SARIF (GitHub Advanced Security / GitLab SAST / Azure DevOps), Markdown, optional PDF via WeasyPrint
- **GitHub Action wrapper** at `aiexponenthq/litmusai/.github/actions/litmusai-screen@v1` for drop-in CI integration

## What this release ships

### Functional requirements

All 37 PRD functional requirements (FR-1 through FR-37) are implemented:
- 8-category screening engine with rule-by-rule trace (`litmus debug`)
- Constrained expression language (no `eval`, no Python execution) with 5 supported function calls
- Per-rule confidence band on every verdict
- Signed-vs-UNREVIEWED ruleset provenance header on every report (FR-36)
- Ruleset diff command (`litmus diff-ruleset <old> <new>`) with rich + JSON output (FR-26)
- Override mechanism with full audit trail (FR-10)
- 5 SARIF rule IDs (one per Article 5 sub-point) for CI integration

### Quality gates

- **257 tests passing** under `pytest --disable-socket` (NFR-8)
- **87.39% coverage** on engine + models (PRD target was ≥ 80%)
- **mypy --strict** clean across 26 source files
- **ruff check** + **ruff format --check** clean across 45 files
- **licensecheck** clean — all 22 production dependencies are Apache / MIT / BSD compatible

### Worked examples

Three reference `system.yaml` files in `examples/` cover the realistic verdict states:

- `example-clear.yaml` → CLEAR overall
- `example-amber.yaml` → AMBER (private-sector credit scoring, 5.1.c needs review)
- `example-red.yaml` → RED (workplace emotion recognition, prohibited under 5.1.f)

Each example is pinned in CI by `tests/integration/test_examples.py` so any future ruleset change that flips an example's verdict surfaces in the next release.

## Legal review status — UNREVIEWED

**LitmusAI 1.0.0 ships with the AiExponent reference ruleset (`ruleset-2024-1689-v1.0`) which is `legal_status: UNREVIEWED`.** The ruleset has been authored and reviewed by an internal AiExponent panel of six engineering and governance roles (see `src/litmusai/_data/ruleset/internal-review-record-2024-1689-v1.0.md`) but has **not** been reviewed by a qualified EU AI Act practising lawyer.

The package version (1.0.0) reflects API stability — the CLI, schema, and BYO-ruleset contracts are stable for production integration. The legal-review status rides on the **ruleset version** plus the explicit `ruleset_legal_status: UNREVIEWED` line printed by `litmus version`. This separates "is the tool stable to integrate?" from "has counsel reviewed the content?" — both questions a procurement reviewer needs answered, and conflating them into a single number loses information either way.

A future `ruleset-2024-1689-v1.1` release will land `legal_status: REVIEWED` once external lawyer review completes. Customers who require lawyer-reviewed output today can supply their own signed ruleset — see [`docs/ruleset-authoring.md`](ruleset-authoring.md) for the BYO mechanism and `tests/fixtures/rulesets/acme-corp-signed-v1.0.json` for a complete worked example.

## Install

```bash
pip install litmusai
```

```bash
# Quick screen from a text description (Steve Jobs critical path)
litmus screen --describe "a chatbot for mental health support for teenagers"

# Or from a structured YAML file
litmus init                    # creates system.yaml template
litmus screen system.yaml
litmus export report.json --format pdf
```

## Disclaimers

> Every screening is a screening, not a certification.
> **Not legal advice. Not a notified body.**

Apache 2.0. AS IS. No warranty of legal compliance.

---

*LitmusAI v1.0.0 · Built by [AI Exponent LLC](https://aiexponent.com) · Apache 2.0*
