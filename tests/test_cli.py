"""Tests for agentict.cli (end-to-end CLI behavior).

These tests exercise the CLI entry point directly (in-process, via
``main(argv)``) rather than spawning a subprocess, to keep the suite fast
and deterministic while still covering the real argument parsing, file I/O,
and exit-code contract described in ``cli.py``'s module docstring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentict import cli
from agentict.disclaimer import DISCLAIMER
from agentict.errors import SourceError
from agentict.models import RawSignal, Verdict, VerdictResult

VALID_WATCHLIST = """# Stock exchange
NASDAQ

# Tickers
- AAPL
"""

MALFORMED_WATCHLIST = """# Stock exchange
NASDAQ

- AAPL
"""


class _FakeSource:
    name = "fake"

    def __init__(self, text: str = "strong growth and record profit", fail: bool = False) -> None:
        self._text = text
        self._fail = fail

    def fetch(self, ticker: str, exchange: str) -> RawSignal:
        if self._fail:
            raise SourceError("simulated failure")
        return RawSignal(source_name=self.name, text=self._text)


class _FakeAnalyst:
    def __init__(self, verdict: Verdict = Verdict.INVEST, rationale: str = "fake") -> None:
        self._verdict = verdict
        self._rationale = rationale

    def assess(self, ticker, exchange, signals):  # noqa: ANN001 - test double
        return VerdictResult(verdict=self._verdict, rationale=self._rationale)


# ---------------------------------------------------------------------------
# AC-1: single one-time run only, no scheduling capability.
# ---------------------------------------------------------------------------


def test_no_scheduling_flags_exist_on_monitor_subcommand() -> None:
    parser = cli.build_arg_parser()
    monitor_parser = parser._subparsers._group_actions[0].choices["monitor"]
    option_strings = {opt for action in monitor_parser._actions for opt in action.option_strings}

    forbidden = {"--schedule", "--interval", "--cron", "--repeat", "--daemon", "--watch"}
    assert forbidden.isdisjoint(option_strings)


def test_only_monitor_subcommand_is_registered() -> None:
    parser = cli.build_arg_parser()
    subparsers_action = parser._subparsers._group_actions[0]
    assert set(subparsers_action.choices) == {"monitor"}


def test_running_monitor_twice_produces_independent_one_time_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Nothing schedules or persists state between invocations."""
    watchlist = tmp_path / "watchlist.md"
    watchlist.write_text(VALID_WATCHLIST, encoding="utf-8")
    monkeypatch.setattr(cli, "enabled_sources", lambda: [_FakeSource()])

    exit_code_1 = cli.main(["monitor", "--file", str(watchlist)])
    output_1 = capsys.readouterr().out
    exit_code_2 = cli.main(["monitor", "--file", str(watchlist)])
    output_2 = capsys.readouterr().out

    assert exit_code_1 == 0
    assert exit_code_2 == 0
    assert output_1 == output_2  # deterministic, no hidden persisted state


# ---------------------------------------------------------------------------
# AC-2: malformed watchlist -> non-zero exit, clear stderr, NO report at all.
# ---------------------------------------------------------------------------


def test_malformed_watchlist_exits_with_usage_error_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    watchlist = tmp_path / "bad.md"
    watchlist.write_text(MALFORMED_WATCHLIST, encoding="utf-8")

    exit_code = cli.main(["monitor", "--file", str(watchlist)])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert captured.err.strip() != ""
    assert "error" in captured.err.lower()
    assert captured.out == ""


def test_malformed_watchlist_with_output_flag_produces_no_report_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    watchlist = tmp_path / "bad.md"
    watchlist.write_text(MALFORMED_WATCHLIST, encoding="utf-8")
    output_path = tmp_path / "report.txt"

    exit_code = cli.main(
        ["monitor", "--file", str(watchlist), "--output", str(output_path)]
    )

    assert exit_code == 2
    assert not output_path.exists()


def test_missing_watchlist_file_exits_with_usage_error_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.md"

    exit_code = cli.main(["monitor", "--file", str(missing)])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err.lower()
    assert captured.out == ""


def test_empty_watchlist_file_is_malformed_and_exits_with_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    watchlist = tmp_path / "empty.md"
    watchlist.write_text("", encoding="utf-8")

    exit_code = cli.main(["monitor", "--file", str(watchlist)])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert captured.err.strip() != ""
    assert captured.out == ""


def test_unknown_analyst_choice_rejected_by_argparse(tmp_path: Path) -> None:
    watchlist = tmp_path / "watchlist.md"
    watchlist.write_text(VALID_WATCHLIST, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        cli.main(["monitor", "--file", str(watchlist), "--analyst", "not-a-real-analyst"])

    # argparse's own usage-error path exits with status 2.
    assert exc_info.value.code == 2


def test_unconfigured_llm_analyst_is_a_usage_error_not_a_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    watchlist = tmp_path / "watchlist.md"
    watchlist.write_text(VALID_WATCHLIST, encoding="utf-8")
    monkeypatch.setattr(cli, "enabled_sources", lambda: [_FakeSource()])

    exit_code = cli.main(["monitor", "--file", str(watchlist), "--analyst", "llm"])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()
    assert captured.out == ""


# ---------------------------------------------------------------------------
# AC-9 / AC-10: successful run renders disclaimer + exact verdict strings.
# ---------------------------------------------------------------------------


def test_successful_run_writes_report_with_disclaimer_and_verdict_to_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    watchlist = tmp_path / "watchlist.md"
    watchlist.write_text(VALID_WATCHLIST, encoding="utf-8")
    monkeypatch.setattr(cli, "enabled_sources", lambda: [_FakeSource()])

    exit_code = cli.main(["monitor", "--file", str(watchlist)])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert DISCLAIMER in captured.out
    assert "AAPL" in captured.out
    assert "NASDAQ" in captured.out
    assert captured.err == ""


def test_successful_run_with_output_flag_writes_file_not_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    watchlist = tmp_path / "watchlist.md"
    watchlist.write_text(VALID_WATCHLIST, encoding="utf-8")
    output_path = tmp_path / "report.txt"
    monkeypatch.setattr(cli, "enabled_sources", lambda: [_FakeSource()])

    exit_code = cli.main(
        ["monitor", "--file", str(watchlist), "--output", str(output_path)]
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == ""  # nothing printed to stdout when --output is used
    assert output_path.exists()
    report_text = output_path.read_text(encoding="utf-8")
    assert DISCLAIMER in report_text
    assert "AAPL" in report_text
