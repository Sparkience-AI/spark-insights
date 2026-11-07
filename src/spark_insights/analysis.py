"""Allowlisted deterministic profiling and supervised analysis operations."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .contracts import (
    AnalysisResult,
    ColumnProfile,
    DatasetProfile,
    MetricResult,
    TaskSpec,
    Warning,
)


class AnalysisError(ValueError):
    """Raised when an explicit analytical contract cannot be satisfied."""


def profile_dataset(frame: pd.DataFrame) -> DatasetProfile:
    """Compute bounded aggregate metadata; never include raw row values."""
    columns: list[ColumnProfile] = []
    for name in frame.columns:
        series = frame[name]
        numeric = (
            pd.to_numeric(series, errors="coerce")
            if pd.api.types.is_numeric_dtype(series)
            else None
        )
        columns.append(
            ColumnProfile(
                name=str(name),
                dtype=str(series.dtype),
                missing_count=int(series.isna().sum()),
                unique_count=int(series.nunique(dropna=True)),
                numeric_min=_finite_or_none(numeric.min()) if numeric is not None else None,
                numeric_max=_finite_or_none(numeric.max()) if numeric is not None else None,
                numeric_mean=_finite_or_none(numeric.mean()) if numeric is not None else None,
            )
        )
    return DatasetProfile(
        row_count=len(frame),
        column_count=len(frame.columns),
        duplicate_row_count=int(frame.duplicated().sum()),
        columns=tuple(columns),
    )


def _finite_or_none(value: object) -> float | None:
    try:
        converted = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return converted if math.isfinite(converted) else None


def _validate_task(frame: pd.DataFrame, task: TaskSpec) -> None:
    if not 0.1 <= task.test_fraction <= 0.5:
        raise AnalysisError("test_fraction must be between 0.1 and 0.5")
    if task.task_type == "profile":
        return
    if not task.target or task.target not in frame.columns:
        raise AnalysisError("A valid target is required for supervised analysis")
    unknown = set(task.exclusions) - set(frame.columns)
    if unknown:
        raise AnalysisError("Every excluded column must exist")
    if task.target in task.exclusions:
        raise AnalysisError("The target cannot be excluded")
    if task.time_column and task.time_column not in frame.columns:
        raise AnalysisError("The configured time column does not exist")
    if task.time_column == task.target:
        raise AnalysisError("The time column cannot also be the target")


def _split(
    frame: pd.DataFrame, task: TaskSpec
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, str]:
    work = frame.copy(deep=True)
    if task.time_column:
        timestamps = pd.to_datetime(work[task.time_column], errors="coerce", utc=True)
        if timestamps.isna().any():
            raise AnalysisError("Time column contains missing or invalid timestamps")
        order = np.argsort(timestamps.to_numpy())
        work = work.iloc[order].reset_index(drop=True)
        strategy = "ordered_holdout"
    else:
        work = work.sample(frac=1, random_state=task.seed).reset_index(drop=True)
        strategy = "seeded_random_holdout"
    split_at = int(len(work) * (1 - task.test_fraction))
    if split_at < 5 or len(work) - split_at < 2:
        raise AnalysisError("Dataset is too small for the requested holdout")
    excluded = set(task.exclusions)
    if task.time_column:
        excluded.add(task.time_column)
    features = [c for c in work.columns if c != task.target and c not in excluded]
    if not features:
        raise AnalysisError("No usable features remain after exclusions")
    assert task.target is not None
    x = work[features]
    y = work[task.target]
    if y.isna().any():
        raise AnalysisError("Target contains missing values")
    return x.iloc[:split_at], x.iloc[split_at:], y.iloc[:split_at], y.iloc[split_at:], strategy


def _preprocessor(x: pd.DataFrame, missing_policy: str) -> ColumnTransformer:
    numeric = list(x.select_dtypes(include=["number", "bool"]).columns)
    categorical = [c for c in x.columns if c not in numeric]
    if missing_policy == "reject" and x.isna().any().any():
        raise AnalysisError("Features contain missing values; select an explicit imputation policy")
    numeric_steps: list[tuple[str, object]] = []
    category_steps: list[tuple[str, object]] = []
    if missing_policy == "train_median_mode":
        numeric_steps.append(("imputer", SimpleImputer(strategy="median")))
        category_steps.append(("imputer", SimpleImputer(strategy="most_frequent")))
    numeric_steps.append(("scale", StandardScaler()))
    category_steps.append(("encode", OneHotEncoder(handle_unknown="ignore")))
    return ColumnTransformer(
        [
            ("numeric", Pipeline(numeric_steps), numeric),
            ("categorical", Pipeline(category_steps), categorical),
        ],
        remainder="drop",
    )


def analyze(frame: pd.DataFrame, task: TaskSpec) -> AnalysisResult:
    """Run one registered deterministic operation from an explicit task spec."""
    _validate_task(frame, task)
    profile = profile_dataset(frame)
    if task.task_type == "profile":
        return AnalysisResult(task_type="profile", target=None, profile=profile)

    x_train, x_test, y_train, y_test, split_strategy = _split(frame, task)
    if len(y_train) < 10:
        raise AnalysisError("At least ten training rows are required")
    preprocess = _preprocessor(x_train, task.missing_policy)
    warnings: list[Warning] = []

    if task.task_type == "regression":
        if not pd.api.types.is_numeric_dtype(y_train):
            raise AnalysisError("Regression target must already be numeric")
        model = Pipeline([("prepare", preprocess), ("model", LinearRegression())])
        baseline = DummyRegressor(strategy="median")
        model.fit(x_train, y_train)
        baseline.fit(np.zeros((len(y_train), 1)), y_train)
        score = float(mean_absolute_error(y_test, model.predict(x_test)))
        baseline_score = float(
            mean_absolute_error(y_test, baseline.predict(np.zeros((len(y_test), 1))))
        )
        if score >= baseline_score:
            warnings.append(
                Warning("baseline_not_beaten", "Model did not beat the median baseline")
            )
        metrics = (MetricResult("mean_absolute_error", score, baseline_score, False),)
        model_name = "linear_regression"
    else:
        if y_train.nunique() < 2:
            raise AnalysisError("Classification target needs at least two training classes")
        model = Pipeline(
            [
                ("prepare", preprocess),
                ("model", LogisticRegression(max_iter=1000, random_state=task.seed)),
            ]
        )
        baseline = DummyClassifier(strategy="most_frequent", random_state=task.seed)
        model.fit(x_train, y_train)
        baseline.fit(np.zeros((len(y_train), 1)), y_train)
        score = float(accuracy_score(y_test, model.predict(x_test)))
        baseline_score = float(accuracy_score(y_test, baseline.predict(np.zeros((len(y_test), 1)))))
        if score <= baseline_score:
            warnings.append(
                Warning("baseline_not_beaten", "Model did not beat the majority baseline")
            )
        metrics = (MetricResult("accuracy", score, baseline_score, True),)
        model_name = "logistic_regression"

    return AnalysisResult(
        task_type=task.task_type,
        target=task.target,
        profile=profile,
        metrics=metrics,
        warnings=tuple(warnings),
        model_name=model_name,
        split_strategy=split_strategy,
    )
