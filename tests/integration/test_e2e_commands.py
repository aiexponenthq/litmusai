"""End-to-end integration tests for all LitmusAI CLI commands.

Spawns real subprocesses using sys.executable so tests exercise the full
import stack, Typer routing, screener engine, exporters, and exit-code
contract — exactly as a user would from a shell.

Acceptance criteria covered:
  AC-12  --help fast (see test_cli_smoke.py)
  AC-16  --describe chatbot/teenagers → amber 5.1.b  (xfail until NLP inference)
  AC-2   calculator → clear
  AC-3   social scoring → red on 5.1.c
  AC-5   verify round-trip
  AC-6   fail-on red → exit 1
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PORTFOLIO_DIR = Path(__file__).parents[1] / "fixtures" / "portfolio"

# Map fixture stem to expected overall verdict — verified against live ruleset.
_EXPECTED_VERDICTS: dict[str, str] = {
    "calculator_clear": "clear",
    "social_scoring_red": "red",
    "workplace_emotion_red": "red",
    "healthcare_emotion_amber": "amber",
    "criminal_risk_red": "red",
    "minors_chatbot_amber": "amber",
    "facial_scraping_red": "red",
    "loan_scorer_amber": "amber",
    "minors_behaviour_red": "red",
    "public_space_biometric_amber": "amber",
}


def _run(*args: str, cwd: Path | None = None, **kwargs: object) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    """Run litmusai as a subprocess and return the CompletedProcess."""
    cmd = [sys.executable, "-m", "litmusai", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=cwd,
        **kwargs,  # type: ignore[arg-type]
    )


def _fixture(name: str) -> Path:
    """Return absolute path to a portfolio fixture file."""
    return _PORTFOLIO_DIR / f"{name}.yaml"


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestE2ECommands:
    # ── 1. litmus init ────────────────────────────────────────────────────

    def test_init_creates_system_yaml(self, tmp_path: Path) -> None:
        """litmus init writes a system.yaml that passes screening with clear."""
        out_file = tmp_path / "system.yaml"
        result = _run("init", "--output", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists(), "system.yaml was not created"
        assert out_file.stat().st_size > 0

    def test_init_created_file_screens_clear(self, tmp_path: Path) -> None:
        """The template produced by litmus init passes screening as clear."""
        out_file = tmp_path / "system.yaml"
        _run("init", "--output", str(out_file))

        report_file = tmp_path / "report.json"
        _run("screen", str(out_file), "--output", str(report_file))
        # returncode may be 0 (clear/amber) — template has all false flags
        assert report_file.exists(), "No report written"
        report = json.loads(report_file.read_text())
        assert report["summary"]["overall_verdict"] == "clear"

    def test_init_refuses_overwrite_without_force(self, tmp_path: Path) -> None:
        """litmus init exits non-zero if output exists and --force not given."""
        out_file = tmp_path / "system.yaml"
        out_file.write_text("existing content")
        result = _run("init", "--output", str(out_file))
        assert result.returncode != 0

    # ── 2. litmus screen <fixture> ────────────────────────────────────────

    def test_screen_calculator_gives_clear(self, tmp_path: Path) -> None:
        """Calculator fixture → overall_verdict: clear."""
        report_file = tmp_path / "report.json"
        result = _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        assert result.returncode == 0, result.stderr
        report = json.loads(report_file.read_text())
        assert report["summary"]["overall_verdict"] == "clear"
        assert report["summary"]["red_count"] == 0
        assert report["summary"]["amber_count"] == 0

    def test_screen_social_scoring_gives_red(self, tmp_path: Path) -> None:
        """Social scoring fixture → overall_verdict: red, triggered in 5.1.c.

        Note: the default --fail-on is "red", so the process exits 1 when the
        verdict is red.  We accept either 0 or 1 here and assert via the report.
        """
        report_file = tmp_path / "report.json"
        result = _run("screen", str(_fixture("social_scoring_red")), "--output", str(report_file))
        # default --fail-on red means returncode is 1 for a red result
        assert result.returncode in (0, 1), result.stderr
        assert report_file.exists(), "Report not written"
        report = json.loads(report_file.read_text())
        assert report["summary"]["overall_verdict"] == "red"
        assert report["categories"]["5.1.c"]["verdict"] == "red"
        assert len(report["categories"]["5.1.c"]["triggered_rules"]) > 0

    # ── 3. litmus screen --describe ───────────────────────────────────────

    def test_screen_describe_teenagers_chatbot_gives_amber(self, tmp_path: Path) -> None:
        """AC-16: --describe mental health chatbot for teenagers → amber on 5.1.b."""
        report_file = tmp_path / "report.json"
        result = _run(
            "screen",
            "--describe",
            "a chatbot for mental health support for teenagers",
            "--output",
            str(report_file),
        )
        assert result.returncode == 0, result.stderr
        assert report_file.exists()
        report = json.loads(report_file.read_text())
        assert report["summary"]["overall_verdict"] == "amber"
        assert report["categories"]["5.1.b"]["verdict"] == "amber"
        assert len(report["categories"]["5.1.b"]["triggered_rules"]) > 0

    def test_screen_describe_returns_zero_exit(self) -> None:
        """--describe always exits 0 when no --fail-on is set."""
        result = _run(
            "screen",
            "--describe",
            "a chatbot for mental health support for teenagers",
        )
        assert result.returncode == 0

    def test_screen_describe_produces_system_quick_screen(self, tmp_path: Path) -> None:
        """--describe embeds system.name == 'Quick Screen' in the report."""
        report_file = tmp_path / "report.json"
        _run(
            "screen",
            "--describe",
            "a basic recommendation engine",
            "--output",
            str(report_file),
        )
        report = json.loads(report_file.read_text())
        assert report["system"]["name"] == "Quick Screen"

    # ── 4. litmus screen <fixture> --output report.json ──────────────────

    def test_screen_output_writes_valid_json(self, tmp_path: Path) -> None:
        """--output flag writes a well-formed JSON report."""
        report_file = tmp_path / "report.json"
        result = _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        assert result.returncode == 0, result.stderr
        assert report_file.exists()
        report = json.loads(report_file.read_text())
        # Check required top-level keys from ScreeningReport schema
        for key in ("report_version", "summary", "categories", "system", "input_hash_sha256"):
            assert key in report, f"Missing key in report: {key!r}"

    def test_screen_output_report_has_all_categories(self, tmp_path: Path) -> None:
        """JSON report contains all 8 Article 5 categories."""
        report_file = tmp_path / "report.json"
        _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        report = json.loads(report_file.read_text())
        expected_cats = {"5.1.a", "5.1.b", "5.1.c", "5.1.d", "5.1.e", "5.1.f", "5.1.g", "5.1.h"}
        assert set(report["categories"].keys()) == expected_cats

    def test_screen_output_report_embeds_system(self, tmp_path: Path) -> None:
        """JSON report embeds the parsed SystemDescription."""
        report_file = tmp_path / "report.json"
        _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        report = json.loads(report_file.read_text())
        assert report["system"]["name"] == "SimpleCalc"

    # ── 5. litmus verify report.json ─────────────────────────────────────

    def test_verify_exits_zero_for_intact_report(self, tmp_path: Path) -> None:
        """litmus verify exits 0 when the report hash matches the embedded system."""
        report_file = tmp_path / "report.json"
        _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        result = _run("verify", str(report_file))
        assert result.returncode == 0, result.stderr
        assert "VERIFIED" in result.stdout

    def test_verify_exits_nonzero_for_tampered_report(self, tmp_path: Path) -> None:
        """litmus verify exits non-zero when the report has been tampered with."""
        report_file = tmp_path / "report.json"
        _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        # Tamper: change the system name in the report
        data = json.loads(report_file.read_text())
        data["system"]["name"] = "TAMPERED"
        report_file.write_text(json.dumps(data))
        result = _run("verify", str(report_file))
        assert result.returncode != 0
        assert "TAMPERED" in result.stderr

    # ── 6. litmus export report.json --format markdown ───────────────────

    def test_export_markdown_creates_file(self, tmp_path: Path) -> None:
        """litmus export --format markdown creates a .md file."""
        report_file = tmp_path / "report.json"
        md_file = tmp_path / "report.md"
        _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        result = _run("export", str(report_file), "--output", str(md_file), "--format", "markdown")
        assert result.returncode == 0, result.stderr
        assert md_file.exists()
        content = md_file.read_text()
        assert len(content) > 0
        # Should contain markdown heading markers
        assert "#" in content

    def test_export_markdown_contains_system_name(self, tmp_path: Path) -> None:
        """Markdown export includes the system name."""
        report_file = tmp_path / "report.json"
        md_file = tmp_path / "report.md"
        _run("screen", str(_fixture("social_scoring_red")), "--output", str(report_file))
        _run("export", str(report_file), "--output", str(md_file), "--format", "markdown")
        content = md_file.read_text()
        assert "CitizenTrustScore" in content

    # ── 7. litmus export report.json --format sarif ───────────────────────

    def test_export_sarif_creates_valid_sarif(self, tmp_path: Path) -> None:
        """litmus export --format sarif creates valid SARIF 2.1.0."""
        report_file = tmp_path / "report.json"
        sarif_file = tmp_path / "report.sarif"
        _run("screen", str(_fixture("social_scoring_red")), "--output", str(report_file))
        result = _run("export", str(report_file), "--output", str(sarif_file), "--format", "sarif")
        assert result.returncode == 0, result.stderr
        assert sarif_file.exists()
        sarif = json.loads(sarif_file.read_text())
        assert sarif.get("version") == "2.1.0"
        assert "$schema" in sarif
        assert "runs" in sarif

    def test_export_sarif_red_fixture_has_results(self, tmp_path: Path) -> None:
        """SARIF export for a RED fixture contains at least one result entry."""
        report_file = tmp_path / "report.json"
        sarif_file = tmp_path / "report.sarif"
        _run("screen", str(_fixture("social_scoring_red")), "--output", str(report_file))
        _run("export", str(report_file), "--output", str(sarif_file), "--format", "sarif")
        sarif = json.loads(sarif_file.read_text())
        results = sarif["runs"][0].get("results", [])
        assert len(results) > 0

    # ── 8. litmus portfolio tests/fixtures/portfolio/ ─────────────────────

    def test_portfolio_screens_all_fixtures(self) -> None:
        """litmus portfolio finds and screens all 10 YAML fixtures without error.

        Rich truncates long file names with an ellipsis, so we assert on the
        system names (which are shorter) rather than the raw filenames.
        """
        result = _run("portfolio", str(_PORTFOLIO_DIR))
        assert result.returncode == 0, f"portfolio failed:\n{result.stderr}"
        # System names always fit within the column width — assert on those.
        expected_system_names = [
            "SimpleCalc",
            "CitizenTrustScore",
            "EmployeeSentimentTracker",
            "ClinicalMoodAssist",
            "RecidivismRiskEngine",
            "TeenTalkBot",
            "FaceVaultDB",
            "LoanRiskScorer",
            "KidsBehaviourPredictor",
            "RetailFaceAnalytics",
        ]
        for name in expected_system_names:
            assert name in result.stdout, f"Expected system name {name!r} in portfolio output"

    def test_portfolio_output_writes_json_array(self, tmp_path: Path) -> None:
        """--output flag on portfolio writes a JSON array of individual reports."""
        out_file = tmp_path / "portfolio.json"
        result = _run("portfolio", str(_PORTFOLIO_DIR), "--output", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists()
        reports = json.loads(out_file.read_text())
        assert isinstance(reports, list)
        assert len(reports) == len(_EXPECTED_VERDICTS)

    def test_portfolio_output_contains_expected_verdicts(self, tmp_path: Path) -> None:
        """Portfolio JSON output matches expected verdicts for each fixture."""
        out_file = tmp_path / "portfolio.json"
        _run("portfolio", str(_PORTFOLIO_DIR), "--output", str(out_file))
        reports = json.loads(out_file.read_text())
        # Build map: system name → verdict
        verdict_map = {r["system"]["name"]: r["summary"]["overall_verdict"] for r in reports}
        # Spot-check a selection of systems
        assert verdict_map["SimpleCalc"] == "clear"
        assert verdict_map["CitizenTrustScore"] == "red"
        assert verdict_map["EmployeeSentimentTracker"] == "red"
        assert verdict_map["ClinicalMoodAssist"] == "amber"
        assert verdict_map["RecidivismRiskEngine"] == "red"
        assert verdict_map["LoanRiskScorer"] == "amber"

    # ── 9. litmus debug report.json ───────────────────────────────────────

    def test_debug_prints_trace(self, tmp_path: Path) -> None:
        """litmus debug prints a rule-firing trace containing category IDs."""
        report_file = tmp_path / "report.json"
        _run("screen", str(_fixture("social_scoring_red")), "--output", str(report_file))
        result = _run("debug", str(report_file))
        assert result.returncode == 0, result.stderr
        # Should print each Article 5 category
        assert "5.1.c" in result.stdout
        assert "red" in result.stdout.lower() or "RED" in result.stdout

    def test_debug_prints_system_name(self, tmp_path: Path) -> None:
        """litmus debug output contains the system name from the report."""
        report_file = tmp_path / "report.json"
        _run("screen", str(_fixture("criminal_risk_red")), "--output", str(report_file))
        result = _run("debug", str(report_file))
        assert result.returncode == 0
        assert "RecidivismRiskEngine" in result.stdout

    def test_debug_clear_fixture_shows_no_triggered_rules(self, tmp_path: Path) -> None:
        """litmus debug on a clear fixture does not print any triggered rule IDs."""
        report_file = tmp_path / "report.json"
        _run("screen", str(_fixture("calculator_clear")), "--output", str(report_file))
        result = _run("debug", str(report_file))
        assert result.returncode == 0
        assert "triggered:" not in result.stdout

    # ── 10. litmus screen <red_fixture> --fail-on red → exit 1 ───────────

    def test_fail_on_red_exits_one_for_red_fixture(self) -> None:
        """--fail-on red exits with code 1 when overall verdict is red."""
        result = _run(
            "screen",
            str(_fixture("social_scoring_red")),
            "--fail-on",
            "red",
        )
        assert result.returncode == 1, (
            f"Expected exit 1 for red verdict with --fail-on red, got {result.returncode}"
        )

    def test_fail_on_red_exits_zero_for_clear_fixture(self) -> None:
        """--fail-on red exits with code 0 when overall verdict is clear."""
        result = _run(
            "screen",
            str(_fixture("calculator_clear")),
            "--fail-on",
            "red",
        )
        assert result.returncode == 0, (
            f"Expected exit 0 for clear verdict with --fail-on red, got {result.returncode}"
        )

    def test_fail_on_red_exits_zero_for_amber_fixture(self) -> None:
        """--fail-on red exits with code 0 when overall verdict is amber (not red)."""
        result = _run(
            "screen",
            str(_fixture("loan_scorer_amber")),
            "--fail-on",
            "red",
        )
        assert result.returncode == 0, (
            f"Expected exit 0 for amber verdict with --fail-on red, got {result.returncode}"
        )

    def test_fail_on_amber_exits_one_for_amber_fixture(self) -> None:
        """--fail-on amber exits with code 1 when overall verdict is amber."""
        result = _run(
            "screen",
            str(_fixture("loan_scorer_amber")),
            "--fail-on",
            "amber",
        )
        assert result.returncode == 1, (
            f"Expected exit 1 for amber verdict with --fail-on amber, got {result.returncode}"
        )

    def test_fail_on_amber_exits_one_for_red_fixture(self) -> None:
        """--fail-on amber exits with code 1 when overall verdict is red (red >= amber)."""
        result = _run(
            "screen",
            str(_fixture("criminal_risk_red")),
            "--fail-on",
            "amber",
        )
        assert result.returncode == 1

    # ── Fixture verdict coverage (parametrised) ───────────────────────────

    @pytest.mark.parametrize(
        "fixture_name,expected_verdict",
        list(_EXPECTED_VERDICTS.items()),
    )
    def test_all_fixtures_produce_expected_verdicts(
        self,
        tmp_path: Path,
        fixture_name: str,
        expected_verdict: str,
    ) -> None:
        """Each portfolio fixture produces its documented expected verdict."""
        report_file = tmp_path / "report.json"
        result = _run(
            "screen",
            str(_fixture(fixture_name)),
            "--output",
            str(report_file),
        )
        # returncode may be 1 if --fail-on red fires; screen always writes the report
        assert report_file.exists(), (
            f"Report not written for {fixture_name}. stderr: {result.stderr}"
        )
        report = json.loads(report_file.read_text())
        actual = report["summary"]["overall_verdict"]
        assert actual == expected_verdict, (
            f"{fixture_name}: expected {expected_verdict!r}, got {actual!r}"
        )
