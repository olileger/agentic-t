"""Command-line entry point for agentict.

    agentict monitor --file <path-to-watchlist>.md [--output <path>] [--analyst heuristic|llm]

Exit codes:
    0 - run completed and a report was emitted (even if all rows are no-data)
    1 - unexpected/unhandled internal error
    2 - usage error: malformed watchlist, missing/unreadable --file, or bad arguments
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agents.factory import get_financial_analyst
from .errors import AgentictError
from .orchestrator import build_report_rows
from .parser import parse_watchlist
from .report import render_report
from .sources.registry import enabled_sources

_EXIT_OK = 0
_EXIT_UNEXPECTED_ERROR = 1
_EXIT_USAGE_ERROR = 2


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentict",
        description="One-time PESTLE signal monitoring for market watchlists.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    monitor = subparsers.add_parser(
        "monitor", help="Run a one-time PESTLE signal scan over a watchlist."
    )
    monitor.add_argument(
        "--file",
        required=True,
        type=Path,
        help="Path to the watchlist markdown file.",
    )
    monitor.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the report to this path instead of stdout.",
    )
    monitor.add_argument(
        "--analyst",
        choices=("heuristic", "llm"),
        default=None,
        help="Financial Analyst implementation to use (default: heuristic, "
        "or AGENTICT_ANALYST environment variable).",
    )
    return parser


def _run_monitor(args: argparse.Namespace) -> int:
    watchlist_path: Path = args.file
    if not watchlist_path.is_file():
        print(f"error: watchlist file not found: {watchlist_path}", file=sys.stderr)
        return _EXIT_USAGE_ERROR

    try:
        text = watchlist_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: could not read watchlist file: {exc}", file=sys.stderr)
        return _EXIT_USAGE_ERROR

    try:
        entries = parse_watchlist(text)
        analyst = get_financial_analyst(args.analyst)
        rows = build_report_rows(entries, enabled_sources(), analyst)
        report_text = render_report(rows)
    except AgentictError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return _EXIT_USAGE_ERROR

    if args.output is not None:
        try:
            args.output.write_text(report_text, encoding="utf-8")
        except OSError as exc:
            print(f"error: could not write report to {args.output}: {exc}", file=sys.stderr)
            return _EXIT_USAGE_ERROR
    else:
        print(report_text, end="")

    return _EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.command == "monitor":
        try:
            return _run_monitor(args)
        except AgentictError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return _EXIT_USAGE_ERROR
        except Exception as exc:  # noqa: BLE001 - top-level CLI safety net
            print(f"unexpected error: {exc}", file=sys.stderr)
            return _EXIT_UNEXPECTED_ERROR

    parser.error(f"unknown command: {args.command}")
    return _EXIT_USAGE_ERROR  # pragma: no cover - argparse.error exits process


if __name__ == "__main__":
    sys.exit(main())
