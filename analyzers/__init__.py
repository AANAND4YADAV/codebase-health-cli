from __future__ import annotations

from pathlib import Path

from analyzers.comments import analyze_comments
from analyzers.complexity import analyze_complexity
from analyzers.duplicates import analyze_duplicates
from analyzers.length import analyze_length
from analyzers.naming import analyze_naming
from analyzers.utils import AnalysisReport, walk_files


def run_all(project_path: Path) -> AnalysisReport:
    """Run all analyzers and return a combined report."""
    files = walk_files(project_path)

    metrics = {
        "complexity": analyze_complexity(project_path, files),
        "length": analyze_length(project_path, files),
        "comments": analyze_comments(project_path, files),
        "duplicates": analyze_duplicates(project_path, files),
        "naming": analyze_naming(project_path, files),
    }

    return AnalysisReport(
        project_path=str(project_path.resolve()),
        files_scanned=len(files),
        metrics=metrics,
    )
