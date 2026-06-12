from __future__ import annotations

import hashlib
from pathlib import Path

from analyzers.utils import MetricResult

WINDOW_SIZE = 6


def _normalize_lines(lines: list[str]) -> list[str]:
    """Strip whitespace and drop blank or pure-comment lines."""
    normalized: list[str] = []
    in_block = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if in_block:
            if "*/" in stripped:
                in_block = False
            continue

        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_block = True
            continue

        if (
            stripped.startswith("//")
            or stripped.startswith("#")
            or stripped.startswith("--")
        ):
            continue

        normalized.append(stripped)

    return normalized


def analyze_duplicates(project_path: Path, files: list[str]) -> MetricResult:
    """Detect duplicate code blocks via hashed sliding windows."""
    hash_locations: dict[str, list[dict[str, int | str]]] = {}
    total_windows = 0

    for rel_path in files:
        full_path = project_path / rel_path
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        normalized = _normalize_lines(source.splitlines())
        if len(normalized) < WINDOW_SIZE:
            continue

        for i in range(len(normalized) - WINDOW_SIZE + 1):
            block = "\n".join(normalized[i : i + WINDOW_SIZE])
            block_hash = hashlib.md5(block.encode()).hexdigest()
            total_windows += 1

            if block_hash not in hash_locations:
                hash_locations[block_hash] = []
            hash_locations[block_hash].append({"file": rel_path, "start_line": i + 1})

    duplicated_windows = sum(
        len(locs) for locs in hash_locations.values() if len(locs) > 1
    )
    duplicate_ratio = duplicated_windows / total_windows if total_windows > 0 else 0.0

    duplicate_groups = [
        {"hash": h, "occurrences": locs, "count": len(locs)}
        for h, locs in hash_locations.items()
        if len(locs) > 1
    ]
    duplicate_groups.sort(key=lambda g: g["count"], reverse=True)

    return MetricResult(
        name="duplicates",
        value=round(duplicate_ratio, 4),
        details={
            "total_windows": total_windows,
            "duplicate_groups": duplicate_groups[:10],
            "duplicate_group_count": len(duplicate_groups),
        },
        offenders=[],
    )
