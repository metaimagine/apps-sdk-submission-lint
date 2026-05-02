"""Command line interface for apps-sdk-submission-lint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

from .manifest import load_manifest
from .rules import Finding, scan_manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        try:
            manifest = load_manifest(args.path)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        findings = scan_manifest(manifest)
        if args.format == "json":
            _write_json(findings, args.path, sys.stdout)
        else:
            _write_text(findings, args.path, sys.stdout)
        return 1 if findings else 0

    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apps-sdk-submission-lint",
        description="Offline lint checks for Apps SDK-style submission metadata.",
    )
    subparsers = parser.add_subparsers(dest="command")
    scan = subparsers.add_parser("scan", help="scan a local JSON manifest")
    scan.add_argument("path", type=Path, help="path to a JSON manifest/app metadata file")
    scan.add_argument("--format", choices=("text", "json"), default="text", help="output format")
    return parser


def _write_json(findings: list[Finding], path: Path, stream: TextIO) -> None:
    payload = {
        "path": str(path),
        "summary": {
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "findings": [finding.to_dict() for finding in findings],
    }
    json.dump(payload, stream, indent=2)
    stream.write("\n")


def _write_text(findings: list[Finding], path: Path, stream: TextIO) -> None:
    stream.write(f"apps-sdk-submission-lint scan: {path}\n")
    if not findings:
        stream.write("No findings.\n")
        return

    stream.write(f"{len(findings)} finding(s)\n\n")
    for finding in findings:
        stream.write(f"[{finding.severity.upper()}] {finding.rule_id} at {finding.path}\n")
        stream.write(f"  {finding.message}\n")
        stream.write(f"  Fix: {finding.help}\n\n")


if __name__ == "__main__":
    raise SystemExit(main())
