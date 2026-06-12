from __future__ import annotations

from pathlib import Path

from analyzers.utils import MetricResult


def _classify_lines(lines: list[str]) -> tuple[int, int]:
    """Return (comment_lines, code_lines) counts."""
    comment_lines = 0
    code_lines = 0
    in_block = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if in_block:
            comment_lines += 1
            if "*/" in stripped:
                in_block = False
            continue

        if stripped.startswith("/*"):
            comment_lines += 1
            if "*/" not in stripped:
                in_block = True
            continue

        if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("--"):
            comment_lines += 1
            continue

        code_lines += 1

    return comment_lines, code_lines


def analyze_comments(project_path: Path, files: list[str]) -> MetricResult:
    """Analyze comment-to-code ratio across source files."""
    total_comments = 0
    total_code = 0
    files_analyzed = 0

    for rel_path in files:
        full_path = project_path / rel_path
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        comments, code = _classify_lines(source.splitlines())
        total_comments += comments
        total_code += code
        files_analyzed += 1

    ratio = total_comments / total_code if total_code > 0 else 0.0

    return MetricResult(
        name="comments",
        value=round(ratio, 4),
        details={
            "comment_lines": total_comments,
            "code_lines": total_code,
            "files_analyzed": files_analyzed,
        },
        offenders=[],
    )
