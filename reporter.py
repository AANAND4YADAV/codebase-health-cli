from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scorer import ScoredReport

METRIC_LABELS = {
    "complexity": "Cyclomatic Complexity",
    "length": "Function Length",
    "comments": "Comment Ratio",
    "duplicates": "Duplicate Code",
    "naming": "Naming Consistency",
}

METRIC_FORMATS = {
    "complexity": lambda v: f"avg CC {v:.2f}",
    "length": lambda v: f"avg {v:.1f} lines",
    "comments": lambda v: f"{v:.2%}",
    "duplicates": lambda v: f"{v:.2%} dup ratio",
    "naming": lambda v: f"{v:.2%} violations",
}

RECOMMENDATIONS = {
    "A": "Excellent codebase health. Keep up the good practices.",
    "B": "Good overall health with minor areas for improvement.",
    "C": "Moderate health. Focus on reducing complexity and duplication.",
    "D": "Below average health. Prioritize refactoring high-complexity functions.",
    "F": "Poor health. Significant refactoring and documentation needed.",
}


def _status_label(score: int) -> str:
    if score >= 16:
        return "Good"
    if score >= 10:
        return "Fair"
    return "Poor"


def _status_style(score: int) -> str:
    if score >= 16:
        return "green"
    if score >= 10:
        return "yellow"
    return "red"


def print_report(report: ScoredReport, console: Console | None = None) -> None:
    """Print a formatted health report to the terminal."""
    console = console or Console()

    header = (
        f"Project: {report.project_path}\n"
        f"Files scanned: {report.files_scanned}\n"
        f"Overall score: {report.total_score}/100  Grade: {report.grade}"
    )
    console.print(Panel(header, title="Codebase Health Report", border_style="blue"))

    table = Table(title="Metric Scores", show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Raw Value")
    table.add_column("Score", justify="center")
    table.add_column("Status", justify="center")

    for key in ("complexity", "length", "comments", "duplicates", "naming"):
        metric = report.metrics[key]
        status = _status_label(metric.score)
        status_text = Text(status, style=_status_style(metric.score))
        table.add_row(
            METRIC_LABELS[key],
            METRIC_FORMATS[key](metric.raw),
            f"{metric.score}/20",
            status_text,
        )

    console.print(table)

    if report.top_offenders:
        offender_table = Table(
            title="Top 5 Worst Functions (by Complexity)",
            show_header=True,
            header_style="bold",
        )
        offender_table.add_column("#", justify="right", style="dim")
        offender_table.add_column("File")
        offender_table.add_column("Line", justify="right")
        offender_table.add_column("Function")
        offender_table.add_column("CC", justify="right", style="red")

        for i, fn in enumerate(report.top_offenders, 1):
            offender_table.add_row(
                str(i),
                fn.file,
                str(fn.line),
                fn.name,
                str(fn.complexity or 0),
            )

        console.print(offender_table)

    console.print(
        Panel(
            RECOMMENDATIONS.get(report.grade, ""),
            title=f"Grade {report.grade}",
            border_style=_status_style(report.metrics["complexity"].score),
        )
    )


def save_json(report: ScoredReport, project_path: Path) -> Path:
    """Save the health report as JSON in the project root."""
    output_path = project_path / "health_report.json"

    payload = {
        "project": report.project_path,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files_scanned": report.files_scanned,
        "total_score": report.total_score,
        "grade": report.grade,
        "metrics": {
            key: {
                "raw": metric.raw,
                "score": metric.score,
                "details": metric.details,
            }
            for key, metric in report.metrics.items()
        },
        "top_offenders": [
            {
                "file": fn.file,
                "line": fn.line,
                "function": fn.name,
                "complexity": fn.complexity,
            }
            for fn in report.top_offenders
        ],
    }

    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path
