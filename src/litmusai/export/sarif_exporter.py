"""SARIF 2.1.0 export for screening reports (FR-29)."""

from __future__ import annotations

from typing import Any


def to_sarif(report: dict[str, Any]) -> dict[str, Any]:
    """Convert a LitmusAI screening report to SARIF 2.1.0 format."""
    rules: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    verdict_to_level = {
        "red": "error",
        "amber": "warning",
        "clear": "note",
    }

    for cat_id, cat in report.get("categories", {}).items():
        rule_id = f"litmusai/{cat_id}"
        rules.append(
            {
                "id": rule_id,
                "name": cat.get("label", cat_id),
                "shortDescription": {"text": f"Article {cat_id} screening"},
                "helpUri": f"https://aiexponent.com/docs/litmusai/article-5#{cat_id}",
            }
        )

        level = verdict_to_level.get(cat.get("verdict", "clear"), "note")
        results.append(
            {
                "ruleId": rule_id,
                "level": level,
                "message": {"text": cat.get("rationale", "")},
                "properties": {
                    "verdict": cat.get("verdict", ""),
                    "confidence": cat.get("confidence", ""),
                    "triggered_rules": cat.get("triggered_rules", []),
                },
            }
        )

    prov = report.get("ruleset_provenance", {})

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "LitmusAI",
                        "version": report.get("litmusai_version", "unknown"),
                        "informationUri": "https://aiexponent.com/products/litmusai",
                        "rules": rules,
                        "properties": {
                            "ruleset_version": report.get("ruleset_version", ""),
                            "ruleset_provenance": prov.get("display_label", ""),
                        },
                    }
                },
                "results": results,
                "properties": {
                    "overall_verdict": report.get("summary", {}).get("overall_verdict", ""),
                    "input_hash_sha256": report.get("input_hash_sha256", ""),
                    "disclaimers": report.get("disclaimers", []),
                },
            }
        ],
    }
