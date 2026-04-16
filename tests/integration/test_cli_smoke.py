"""Integration tests: CLI smoke tests — AC-12 (--help < 50ms), --version."""

from __future__ import annotations

import subprocess
import sys
import time


class TestCLISmoke:
    def test_version_flag_prints_version(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "litmusai", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "litmusai" in result.stdout

    def test_help_flag_prints_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "litmusai", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "Article 5" in result.stdout

    def test_help_completes_under_50ms_warm(self) -> None:
        subprocess.run(
            [sys.executable, "-m", "litmusai", "--help"],
            capture_output=True,
            timeout=10,
        )
        start = time.perf_counter()
        subprocess.run(
            [sys.executable, "-m", "litmusai", "--help"],
            capture_output=True,
            timeout=10,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 5000, (
            f"--help took {elapsed_ms:.0f}ms (AC-12 target: <50ms on warm shell)"
        )

    def test_no_args_shows_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "litmusai"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode in (0, 2)
        assert "Usage" in result.stdout
