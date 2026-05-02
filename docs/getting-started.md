# Getting Started with LitmusAI

## Installation

```bash
pip install litmus-screener
```

The product brand is **LitmusAI**; the PyPI distribution name is `litmus-screener` (PEP 541 collision with an unrelated package on `litmus-ai` / `litmusai`). After install the CLI entry point is `litmus` and the Python module is `litmusai`.

Requires Python 3.11+. No API keys, no sign-ups, no network access.

## Quick Screen (20 seconds)

```bash
litmus screen --describe "a chatbot for mental health support for teenagers"
```

LitmusAI infers system characteristics from your description and screens against all 8 Article 5 categories.

## Full Screen (structured YAML)

```bash
# 1. Create a system description template
litmus init

# 2. Edit system.yaml with your system details
# 3. Run the screening
litmus screen system.yaml

# 4. Export the report
litmus screen system.yaml --output report.json
litmus export report.json --output report.md --format markdown
```

## Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| **CLEAR** | No Article 5 indicators detected | Document and proceed |
| **AMBER** | Potential indicators — ambiguous | Get legal review before deployment |
| **RED** | System likely falls within a prohibition | Do not deploy without qualified counsel |

## CI/CD Integration

```bash
# Fail the build on any red verdict
litmus screen system.yaml --fail-on red

# Fail on amber or worse
litmus screen system.yaml --fail-on amber
```

## Next Steps

- [Article 5 Coverage](article-5-coverage.md) — what each category means
- [Ruleset Authoring](ruleset-authoring.md) — bring your own lawyer-signed ruleset
- [CI Integration](ci-integration.md) — GitHub Action setup

---

*Not legal advice. Not a notified body.*
