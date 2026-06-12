from __future__ import annotations

from dataclasses import dataclass, field

from analyzers.utils import AnalysisReport, FunctionInfo, MetricResult


@dataclass
class ScoredMetric:
    name: str
    raw: float
    score: int
    details: dict = field(default_factory=dict)
    offenders: list[FunctionInfo] = field(default_factory=list)


@dataclass
class ScoredReport:
    project_path: str
    files_scanned: int
    metrics: dict[str, ScoredMetric]
    total_score: int
    grade: str
    top_offenders: list[FunctionInfo] = field(default_factory=list)


def _score_complexity(avg_cc: float) -> int:
    if avg_cc <= 3:
        return 20
    if avg_cc <= 5:
        return 16
    if avg_cc <= 8:
        return 12
    if avg_cc <= 12:
        return 8
    return 4


def _score_length(avg_lines: float) -> int:
    if avg_lines <= 15:
        return 20
    if avg_lines <= 25:
        return 16
    if avg_lines <= 40:
        return 12
    if avg_lines <= 60:
        return 8
    return 4


def _score_comments(ratio: float) -> int:
    if ratio >= 0.25:
        return 20
    if ratio >= 0.15:
        return 16
    if ratio >= 0.08:
        return 12
    if ratio >= 0.03:
        return 8
    return 4


def _score_duplicates(dup_ratio: float) -> int:
    if dup_ratio <= 0.02:
        return 20
    if dup_ratio <= 0.05:
        return 16
    if dup_ratio <= 0.10:
        return 12
    if dup_ratio <= 0.20:
        return 8
    return 4


def _score_naming(violation_rate: float) -> int:
    if violation_rate <= 0.02:
        return 20
    if violation_rate <= 0.05:
        return 16
    if violation_rate <= 0.10:
        return 12
    if violation_rate <= 0.20:
        return 8
    return 4


SCORERS = {
    "complexity": _score_complexity,
    "length": _score_length,
    "comments": _score_comments,
    "duplicates": _score_duplicates,
    "naming": _score_naming,
}


def _letter_grade(total: int) -> str:
    if total >= 90:
        return "A"
    if total >= 80:
        return "B"
    if total >= 70:
        return "C"
    if total >= 60:
        return "D"
    return "F"


def _score_metric(metric: MetricResult) -> ScoredMetric:
    scorer = SCORERS[metric.name]
    return ScoredMetric(
        name=metric.name,
        raw=metric.value,
        score=scorer(metric.value),
        details=metric.details,
        offenders=metric.offenders,
    )


def score_report(analysis: AnalysisReport) -> ScoredReport:
    """Convert raw analysis results into scored metrics and a letter grade."""
    scored_metrics = {
        name: _score_metric(metric) for name, metric in analysis.metrics.items()
    }
    total = sum(m.score for m in scored_metrics.values())

    complexity_offenders = analysis.metrics.get("complexity")
    top_offenders: list[FunctionInfo] = []
    if complexity_offenders:
        top_offenders = complexity_offenders.offenders[:5]

    return ScoredReport(
        project_path=analysis.project_path,
        files_scanned=analysis.files_scanned,
        metrics=scored_metrics,
        total_score=total,
        grade=_letter_grade(total),
        top_offenders=top_offenders,
    )
