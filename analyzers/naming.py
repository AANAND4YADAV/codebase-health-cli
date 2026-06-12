from __future__ import annotations

import ast
import re
from pathlib import Path

from analyzers.utils import FunctionInfo, MetricResult

SNAKE_CASE = re.compile(r"^[a-z_][a-z0-9_]*$")
DUNDER_PATTERN = re.compile(r"^__\w+__$")


def _is_valid_snake_case(name: str) -> bool:
    if DUNDER_PATTERN.match(name):
        return True
    if name == "_":
        return True
    if name.isupper():
        return True
    return bool(SNAKE_CASE.match(name))


def _check_names(tree: ast.AST, rel_path: str) -> tuple[list[FunctionInfo], int]:
    violations: list[FunctionInfo] = []
    checked = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            checked += 1
            if not _is_valid_snake_case(node.name):
                violations.append(
                    FunctionInfo(name=node.name, file=rel_path, line=node.lineno)
                )

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    checked += 1
                    if not _is_valid_snake_case(target.id):
                        violations.append(
                            FunctionInfo(
                                name=target.id,
                                file=rel_path,
                                line=node.lineno,
                            )
                        )

    return violations, checked


def analyze_naming(project_path: Path, files: list[str]) -> MetricResult:
    """Check snake_case naming consistency in Python files."""
    all_violations: list[FunctionInfo] = []
    total_checked = 0
    py_files = [f for f in files if f.endswith(".py")]

    for rel_path in py_files:
        full_path = project_path / rel_path
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        violations, checked = _check_names(tree, rel_path)
        all_violations.extend(violations)
        total_checked += checked

    violation_rate = len(all_violations) / total_checked if total_checked > 0 else 0.0

    return MetricResult(
        name="naming",
        value=round(violation_rate, 4),
        details={
            "names_checked": total_checked,
            "violations": len(all_violations),
            "python_files": len(py_files),
        },
        offenders=all_violations,
    )
