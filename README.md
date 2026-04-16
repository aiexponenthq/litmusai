<p align="center">
  <a href="https://aiexponent.com"><img src=".github/brand/logo-full-light.png" alt="AiExponent — Building AI that deserves to be trusted" width="560"></a>
</p>

<h1 align="center">LitmusAI</h1>
<p align="center"><em>Free, deterministic Article 5 screener for the EU AI Act.</em></p>

<p align="center">
  <a href="https://pypi.org/project/litmusai/"><img src="https://img.shields.io/pypi/v/litmusai.svg" alt="PyPI"></a>
  <a href="https://github.com/aiexponenthq/litmusai/actions"><img src="https://github.com/aiexponenthq/litmusai/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-0D5463.svg" alt="License: Apache 2.0"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11%2B-0D5463.svg" alt="Python 3.11+"></a>
  <a href="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689"><img src="https://img.shields.io/badge/EU%20AI%20Act-Article%205-0D5463.svg" alt="EU AI Act Article 5"></a>
  <a href="#privacy"><img src="https://img.shields.io/badge/telemetry-zero-0B7A4B.svg" alt="Zero telemetry"></a>
</p>

---

Screen your AI system against the **eight prohibited-practice categories** of [Article 5](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689) of the EU AI Act (Regulation (EU) 2024/1689). Get a per-category **Red / Amber / Clear** verdict with regulatory citations, confidence levels, and remediation guidance — in under 60 seconds, without a sales call, without a paywall, and without uploading data to any server.

Built by [AiExponent LLC](https://aiexponent.com). Apache 2.0. Runs entirely offline after `pip install`.

## Quick Start

```bash
pip install litmusai
```

```bash
# Quick screen from a text description
litmus screen --describe "a chatbot for mental health support for teenagers"

# Or from a structured YAML file
litmus init                    # creates system.yaml template
litmus screen system.yaml      # full screening with all 8 categories
litmus export report.json --format pdf
```

## What LitmusAI Does

- Screens AI systems against all 8 categories of Article 5(1)(a)–(h)
- Produces **deterministic** verdicts: same input → same output, always
- Generates audit-ready reports (JSON, SARIF, Markdown, PDF)
- Runs in CI/CD as a pre-merge gate (GitHub Action included)
- Works **fully offline** — zero network calls, zero telemetry
- Supports **Bring-Your-Own-Ruleset** — plug in your lawyer's signed interpretation

## Important Disclaimers

> **UNREVIEWED REFERENCE RULESET**
>
> The default LitmusAI ruleset (`aiexponent-reference-v1.0`) is a good-faith engineering interpretation of Article 5, authored by AiExponent's internal compliance panel. **It has not been reviewed or signed by a qualified EU AI Act lawyer and is not legal advice.**
>
> If your organisation needs a lawyer-signed ruleset, see [docs/ruleset-authoring.md](docs/ruleset-authoring.md) for the BYO-ruleset path.
>
> Every screening is a screening, not a certification. **Not legal advice. Not a notified body.**

## Privacy

<a name="privacy"></a>

LitmusAI makes **zero network calls** during screening. No telemetry, no usage metrics, no crash reports. Your system descriptions never leave your machine. Enforced in CI via `pytest-socket --disable-socket`.

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

<div align="center">
  <sub>
    <a href="https://aiexponent.com">aiexponent.com</a> ·
    <a href="mailto:hello@aiexponent.com">hello@aiexponent.com</a> ·
    Built in the open · Apache 2.0
  </sub>
</div>
