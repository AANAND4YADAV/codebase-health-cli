from __future__ import annotations

import ast
import re
from pathlib import Path

from analyzers.utils import FunctionInfo, MetricResult

FUNCTION_PATTERNS = [
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)"),
    re.compile(r"^\s*(?:public|private|protected|static|async|virtual|\s)*\s*\w+\s+(\w+)\s*\([^)]*\)\s*\{"),
    re.compile(r"^\s*fn\s+(\w+)"),
    re.compile(r"^\s*func\s+(\w+)"),
    re.compile(r"^\s*(?:public|private|protected|static|\s)*\w+\s+(\w+)\s*\([^)]*\)\s*\{"),
]


def _python_functions(source: str, rel_path: str) -> list[FunctionInfo]:
    functions: list[FunctionInfo] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return functions

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, "end_lineno", None) or node.lineno
            length = end_line - node.lineno + 1
            functions.append(
                FunctionInfo(
                    name=node.name,
                    file=rel_path,
                    line=node.lineno,
                    length=length,
                )
            )
    return functions


def _heuristic_functions(lines: list[str], rel_path: str) -> list[FunctionInfo]:
    """Best-effort function length detection for non-Python files."""
    functions: list[FunctionInfo] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched_name = None
        for pattern in FUNCTION_PATTERNS:
            match = pattern.match(line)
            if match:
                matched_name = match.group(1)
                break

        if matched_name is None:
            i += 1
            continue

        start = i
        brace_depth = line.count("{") - line.count("}")
        j = i + 1
        while j < len(lines) and brace_depth > 0:
            brace_depth += lines[j].count("{") - lines[j].count("}")
            j += 1

        if brace_depth > 0:
            j = min(i + 100, len(lines))

        functions.append(
            FunctionInfo(
                name=matched_name,
                file=rel_path,
                line=start + 1,
                length=j - start,
            )
        )
        i = j

    return functions


def analyze_length(project_path: Path, files: list[str]) -> MetricResult:
    """Analyze average function length in lines."""
    all_functions: list[FunctionInfo] = []

    for rel_path in files:
        full_path = project_path / rel_path
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if rel_path.endswith(".py"):
            all_functions.extend(_python_functions(source, rel_path))
        else:
            all_functions.extend(_heuristic_functions(source.splitlines(), rel_path))

    all_functions.sort(key=lambda f: f.length or 0, reverse=True)

    if all_functions:
        avg_length = sum(f.length or 0 for f in all_functions) / len(all_functions)
    else:
        avg_length = 0.0

    return MetricResult(
        name="length",
        value=round(avg_length, 2),
        details={"functions_analyzed": len(all_functions)},
        offenders=all_functions,
    )
