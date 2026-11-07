from __future__ import annotations

import pandas as pd
import pytest

from spark_insights.analysis import AnalysisError, analyze
from spark_insights.contracts import TaskSpec


def regression_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "when": pd.date_range("2025-01-01", periods=60, freq="D").astype(str),
            "x": list(range(60)),
            "group": ["a", "b"] * 30,
            "y": [2 * value + 3 for value in range(60)],
        }
    )


def test_profile_is_aggregate_only() -> None:
    result = analyze(regression_frame(), TaskSpec())
    assert result.profile.row_count == 60
    assert result.metrics == ()
    assert result.target is None


def test_regression_uses_time_holdout_and_beats_baseline() -> None:
    result = analyze(
        regression_frame(),
        TaskSpec(task_type="regression", target="y", time_column="when", exclusions=("group",)),
    )
    assert result.split_strategy == "ordered_holdout"
    assert result.metrics[0].value < result.metrics[0].baseline_value
    assert result.model_name == "linear_regression"


def test_classification_is_seed_deterministic() -> None:
    frame = regression_frame().drop(columns=["y", "when"])
    frame["label"] = ["low" if value < 30 else "high" for value in frame["x"]]
    task = TaskSpec(task_type="classification", target="label", seed=7)
    first = analyze(frame, task)
    second = analyze(frame, task)
    assert first.metrics == second.metrics


def test_missing_values_require_explicit_policy() -> None:
    frame = regression_frame()
    frame.loc[4, "x"] = None
    with pytest.raises(AnalysisError, match="missing values"):
        analyze(frame, TaskSpec(task_type="regression", target="y"))
    result = analyze(
        frame,
        TaskSpec(task_type="regression", target="y", missing_policy="train_median_mode"),
    )
    assert result.metrics


def test_target_and_time_semantics_are_explicit() -> None:
    with pytest.raises(AnalysisError, match="target"):
        analyze(regression_frame(), TaskSpec(task_type="regression"))
    bad = regression_frame()
    bad.loc[0, "when"] = "not-a-date"
    with pytest.raises(AnalysisError, match="timestamps"):
        analyze(bad, TaskSpec(task_type="regression", target="y", time_column="when"))
