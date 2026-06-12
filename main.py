#!/usr/bin/env python3
"""codebase-health: Analyze a project folder and generate a health report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyzers import run_all
from analyzers.utils import walk_files
from reporter import print_report, save_json
from scorer import score_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a project folder and generate a codebase health report.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project folder to analyze (default: current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(f"Error: path does not exist: {project_path}", file=sys.stderr)
        return 1

    if not project_path.is_dir():
        print(f"Error: path is not a directory: {project_path}", file=sys.stderr)
        return 1

    files = walk_files(project_path)
    if not files:
        print(f"Error: no scannable source files found in {project_path}", file=sys.stderr)
        return 1

    analysis = run_all(project_path)
    scored = score_report(analysis)

    print_report(scored)
    json_path = save_json(scored, project_path)
    print(f"\nReport saved to {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
