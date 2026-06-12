from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".swift",
    ".kt",
    ".scala",
    ".sh",
    ".sql",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".md",
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "eggs",
    ".eggs",
}


@dataclass
class FunctionInfo:
    name: str
    file: str
    line: int
    complexity: int | None = None
    length: int | None = None


@dataclass
class MetricResult:
    name: str
    value: float
    details: dict = field(default_factory=dict)
    offenders: list[FunctionInfo] = field(default_factory=list)


@dataclass
class AnalysisReport:
    project_path: str
    files_scanned: int
    metrics: dict[str, MetricResult]


def walk_files(root: Path, extensions: set[str] | None = None) -> list[str]:
    """Yield relative file paths under root, skipping common noise directories."""
    root = root.resolve()
    if extensions is None:
        extensions = SOURCE_EXTENSIONS

    results: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in extensions:
            continue
        results.append(str(path.relative_to(root)).replace("\\", "/"))
    return sorted(results)
