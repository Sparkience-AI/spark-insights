"""Deterministic, self-contained HTML reporting from typed results."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .contracts import AnalysisResult


def _metric_chart(result: AnalysisResult) -> str:
    if not result.metrics:
        return "<p>No supervised metric was requested.</p>"
    parts: list[str] = []
    for metric in result.metrics:
        maximum = max(abs(metric.value), abs(metric.baseline_value), 1e-12)
        model_width = min(100.0, 100 * abs(metric.value) / maximum)
        baseline_width = min(100.0, 100 * abs(metric.baseline_value) / maximum)
        parts.append(
            f"<h3>{escape(metric.name)}</h3>"
            f"<p>Model: {metric.value:.6g}; baseline: {metric.baseline_value:.6g}</p>"
            f'<div class="bar model" style="width:{model_width:.2f}%">model</div>'
            f'<div class="bar baseline" style="width:{baseline_width:.2f}%">baseline</div>'
        )
    return "".join(parts)


def write_html_report(result: AnalysisResult, destination: Path) -> None:
    """Write a portable report containing only validated aggregates."""
    warnings = (
        "".join(
            f"<li><strong>{escape(item.code)}</strong>: {escape(item.message)}</li>"
            for item in result.warnings
        )
        or "<li>None recorded.</li>"
    )
    column_rows = "".join(
        "<tr>"
        f"<td>{escape(column.name)}</td><td>{escape(column.dtype)}</td>"
        f"<td>{column.missing_count}</td><td>{column.unique_count}</td>"
        "</tr>"
        for column in result.profile.columns
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Spark Insights analysis report</title><style>
body{{font:16px system-ui;max-width:960px;margin:2rem auto;padding:0 1rem;color:#172033}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccd3df;padding:.5rem;text-align:left}}
.bar{{color:white;padding:.35rem;min-width:4rem;margin:.3rem 0}}.model{{background:#3157c8}}.baseline{{background:#687386}}
</style></head><body><main><h1>Spark Insights analysis report</h1>
<p>Task: <strong>{escape(result.task_type)}</strong>. Rows: {result.profile.row_count}. Columns: {result.profile.column_count}. Duplicate rows: {result.profile.duplicate_row_count}.</p>
<h2>Validated metric comparison</h2>{_metric_chart(result)}
<h2>Warnings and limitations</h2><ul>{warnings}</ul>
<h2>Schema profile</h2><table><thead><tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th></tr></thead><tbody>{column_rows}</tbody></table>
<p>This report contains computed aggregates, not causal conclusions or automated business recommendations.</p>
</main></body></html>"""
    destination.write_text(html, encoding="utf-8")
