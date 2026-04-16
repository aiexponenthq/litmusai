# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.x     | Yes (current dev)  |

## Reporting a Vulnerability

If you discover a security vulnerability in LitmusAI, please report it responsibly:

1. **Email:** security@aiexponent.com
2. **Subject line:** `[LitmusAI Security] <brief description>`
3. **Do not** open a public GitHub issue for security vulnerabilities.

We will acknowledge receipt within 48 hours and provide an initial assessment within 5 business days.

## False-Negative Reports

If you believe LitmusAI's reference ruleset produces a **wrongly Clear verdict** on a system that should be flagged under Article 5, this is a **critical safety issue**. Please report it using the same process above with the subject line `[LitmusAI False Negative] <category>`.

## Scope

- Expression evaluator (`engine/expression.py`) — any code execution outside the whitelist
- YAML parsing — any bypass of `yaml.safe_load`
- Ruleset signature verification — any bypass of signature validation
- Input hash integrity — any collision or canonicalisation failure

## Out of Scope

- Disagreements about the legal interpretation of Article 5 text (use the BYO-ruleset path instead)
- Feature requests
