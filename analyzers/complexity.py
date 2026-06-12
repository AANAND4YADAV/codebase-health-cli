from __future__ import annotations

from pathlib import Path

from radon.complexity import cc_visit
from radon.visitors import Function

from analyzers.utils import FunctionInfo, MetricResult


def _iter_functions(blocks) -> list[Function]:
    """Flatten Function blocks, including nested closures. Skip Class blocks."""
    functions: list[Function] = []
    for block in blocks:
        if isinstance(block, Function):
            functions.append(block)
            functions.extend(block.closures)
    return functions


def _function_name(block: Function) -> str:
    if block.classname:
        return f"{block.classname}.{block.name}"
    return block.name


def analyze_complexity(project_path: Path, files: list[str]) -> MetricResult:
    """Analyze cyclomatic complexity per function using radon (Python only)."""
    offenders: list[FunctionInfo] = []
    py_files = [f for f in files if f.endswith(".py")]

    for rel_path in py_files:
        full_path = project_path / rel_path
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        try:
            blocks = cc_visit(source)
        except Exception:
            continue

        for block in _iter_functions(blocks):
            offenders.append(
                FunctionInfo(
                    name=_function_name(block),
                    file=rel_path,
                    line=block.lineno,
                    complexity=block.complexity,
                )
            )

    offenders.sort(key=lambda f: f.complexity or 0, reverse=True)

    if offenders:
        avg_cc = sum(f.complexity or 0 for f in offenders) / len(offenders)
    else:
        avg_cc = 0.0

    return MetricResult(
        name="complexity",
        value=round(avg_cc, 2),
        details={
            "functions_analyzed": len(offenders),
            "python_files": len(py_files),
        },
        offenders=offenders,
    )
