# Bring Your Own Ruleset (BYO)

LitmusAI ships with a reference ruleset authored by AiExponent's internal panel. If your organisation needs a lawyer-signed interpretation, you can author your own.

## Ruleset Schema

A ruleset is a JSON file with this structure:

```json
{
  "ruleset_version": "your-org-v1.0",
  "regulation": "Regulation (EU) 2024/1689",
  "effective_date": "2025-02-02",
  "rules": [...],
  "signature": { ... }  // optional
}
```

### Rule format

```json
{
  "id": "rule_a_your_rule_name",
  "category": "5.1.a",
  "version": "v1",
  "description": "Human-readable description of what this rule checks.",
  "expression": "system.inputs.biometric == true and system.outputs.behaviour_predictions == true",
  "verdict_if_triggered": "amber",
  "citations": ["Art. 5(1)(a)", "Recital 29"],
  "reviewed_by": "Your Law Firm LLP",
  "reviewed_date": "2026-05-01"
}
```

### Expression language

Rules use a constrained expression language (not Python). Supported:

- **Field access:** `system.inputs.biometric`, `system.outputs.individual_scores`
- **Comparisons:** `==`, `!=`
- **Boolean:** `and`, `or`, `not`
- **Set membership:** `"value" in system.mitigations`
- **Functions:** `contains()`, `starts_with()`, `has_jurisdiction()`, `targets_population()`
- **Parentheses:** `(a or b) and c`

### Signature block (optional)

```json
{
  "signer_name": "Smith & Co LLP",
  "signer_bar_number": "BAR-EU-12345",
  "signer_firm": "Smith & Co LLP",
  "signer_email": "partners@smithco.example",
  "signed_date": "2026-05-01",
  "signature_algorithm": "sha256",
  "signature_value": "hex-encoded-hash"
}
```

Supported algorithms: `sha256`, `pgp-detached`, `x509-pkcs7`.

## Using Your Ruleset

```bash
# Validate the ruleset
litmus verify-ruleset your-ruleset.json

# Set as active
litmus use-ruleset your-ruleset.json

# Screen with it
litmus screen system.yaml --ruleset your-ruleset.json

# Check what's active
litmus ruleset-info
```

## Provenance in Reports

When using a signed ruleset, every report header shows:

```
ruleset: your-org-v1.0 (SIGNED by: Smith & Co LLP · 2026-05-01 · signature verified)
```

When using the default reference ruleset:

```
ruleset: aiexponent-reference-v1.0 (UNREVIEWED — internal panel authored, no external legal review)
```

---

*Not legal advice. Not a notified body.*
