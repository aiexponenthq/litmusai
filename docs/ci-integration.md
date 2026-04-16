# CI/CD Integration

## GitHub Action

```yaml
name: Article 5 Screening
on: [pull_request]

jobs:
  litmusai:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aiexponenthq/litmusai/.github/actions/litmusai-screen@v1
        with:
          path: ai-system.yaml
          fail-on: amber
```

## CLI in any CI

```bash
pip install litmusai
litmus screen system.yaml --fail-on red --output report.json --quiet
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clear or below `--fail-on` threshold |
| 1 | Threshold exceeded (red or amber, depending on `--fail-on`) |
| 2 | Invalid input / schema error |
| 3 | Tamper detected (`verify` command) |

## SARIF for GitHub Code Scanning

```bash
litmus screen system.yaml --output report.json
litmus export report.json --output report.sarif --format sarif
```

Upload `report.sarif` to GitHub Advanced Security Code Scanning. Each Article 5 category maps to a SARIF rule. Red = error, Amber = warning, Clear = note.

## Portfolio Screening

```bash
litmus portfolio ./systems/ --output portfolio-report.json
```

Screens every `.yaml` file in a directory.

---

*Not legal advice. Not a notified body.*
