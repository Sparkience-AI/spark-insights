"""Typed, JSON-serializable contracts for deterministic analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["info", "warning", "error"]
TaskType = Literal["profile", "regression", "classification"]


@dataclass(frozen=True)
class Limits:
    max_bytes: int = 20_000_000
    max_rows: int = 100_000
    max_columns: int = 250
    max_sheets: int = 10


@dataclass(frozen=True)
class DatasetFingerprint:
    sha256: str
    byte_count: int
    format: str
    encoding: str | None = None


@dataclass(frozen=True)
class ColumnProfile:
    name: str
    dtype: str
    missing_count: int
    unique_count: int
    numeric_min: float | None = None
    numeric_max: float | None = None
    numeric_mean: float | None = None


@dataclass(frozen=True)
class DatasetProfile:
    row_count: int
    column_count: int
    duplicate_row_count: int
    columns: tuple[ColumnProfile, ...]


@dataclass(frozen=True)
class TaskSpec:
    task_type: TaskType = "profile"
    target: str | None = None
    exclusions: tuple[str, ...] = ()
    time_column: str | None = None
    units: str | None = None
    seed: int = 42
    test_fraction: float = 0.2
    missing_policy: Literal["reject", "train_median_mode"] = "reject"


@dataclass(frozen=True)
class Warning:
    code: str
    message: str
    severity: Severity = "warning"


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: float
    baseline_value: float
    higher_is_better: bool


@dataclass(frozen=True)
class AnalysisResult:
    task_type: TaskType
    target: str | None
    profile: DatasetProfile
    metrics: tuple[MetricResult, ...] = ()
    warnings: tuple[Warning, ...] = ()
    limitations: tuple[str, ...] = ()
    model_name: str | None = None
    split_strategy: str | None = None


@dataclass(frozen=True)
class ArtifactRecord:
    kind: str
    relative_path: str
    sha256: str
    byte_count: int


@dataclass(frozen=True)
class RunManifest:
    schema_version: str
    run_id: str
    created_at_utc: str
    method_version: str
    package_version: str
    source_revision: str
    runtime_versions: dict[str, str]
    dependency_versions: dict[str, str]
    reproducibility_hash: str
    result_hash: str
    dataset: DatasetFingerprint
    task: TaskSpec
    result: AnalysisResult
    approvals: dict[str, bool]
    manifest_warnings: tuple[str, ...] = field(default_factory=tuple)
    artifacts: tuple[ArtifactRecord, ...] = field(default_factory=tuple)
    provider: str | None = None
    provider_model: str | None = None


Contract = (
    Limits
    | DatasetFingerprint
    | ColumnProfile
    | DatasetProfile
    | TaskSpec
    | Warning
    | MetricResult
    | AnalysisResult
    | ArtifactRecord
    | RunManifest
)


def to_dict(value: Contract) -> dict[str, Any]:
    """Convert a contract to a JSON-safe dictionary."""
    return asdict(value)
