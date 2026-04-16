# LitmusAI Screen — GitHub Action

Screen an AI system against Article 5 of the EU AI Act as a CI/CD gate.

## Usage

```yaml
- uses: aiexponenthq/litmusai/.github/actions/litmusai-screen@v1
  with:
    path: system.yaml
    fail-on: amber  # or: red, none
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `path` | Yes | — | Path to system.yaml |
| `fail-on` | No | `red` | Fail on this verdict or worse |
| `output-format` | No | `json` | Output format: json or sarif |
| `ruleset` | No | — | Path to custom ruleset |
| `python-version` | No | `3.11` | Python version |

## Outputs

| Output | Description |
|--------|-------------|
| `verdict` | Overall verdict: clear, amber, red |
| `report-path` | Path to generated report |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clear or below fail-on threshold |
| 1 | Threshold exceeded |
| 2 | Invalid input / schema error |

## Example: Fail PR on amber

```yaml
name: Article 5 Screening
on: [pull_request]
jobs:
  screen:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aiexponenthq/litmusai/.github/actions/litmusai-screen@v1
        with:
          path: ai-system.yaml
          fail-on: amber
```

Not legal advice. Not a notified body.
