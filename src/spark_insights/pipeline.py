"""Trusted orchestration plane for one isolated analysis run."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
from dataclasses import replace
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

from . import __version__
from .analysis import analyze
from .contracts import ArtifactRecord, Limits, RunManifest, TaskSpec, to_dict
from .ingestion import load_dataset
from .providers import NarrationRequest, ProviderClient, narrate
from .reporting import write_html_report

METHOD_VERSION = "deterministic-tabular-v2"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _artifact(path: Path, root: Path, kind: str) -> ArtifactRecord:
    data = path.read_bytes()
    return ArtifactRecord(
        kind=kind,
        relative_path=path.relative_to(root).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),
        byte_count=len(data),
    )


def _hash_json(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _execution_identity(source_revision: str | None) -> tuple[str, dict[str, str], dict[str, str]]:
    revision = (
        source_revision
        if source_revision is not None
        else os.environ.get("SPARK_INSIGHTS_SOURCE_REVISION")
    )
    if revision is None:
        revision = "unavailable"
    if not revision.strip():
        raise ValueError("Source revision cannot be blank.")
    runtime_versions = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
    }
    dependency_versions = {
        "spark-insights": __version__,
        "numpy": version("numpy"),
        "pandas": version("pandas"),
        "scikit-learn": version("scikit-learn"),
        "openpyxl": version("openpyxl"),
    }
    return revision, runtime_versions, dependency_versions


def run_analysis(
    source: Path,
    *,
    allowed_root: Path,
    output_root: Path,
    task: TaskSpec,
    limits: Limits | None = None,
    sheet_name: str | None = None,
    encoding: str = "utf-8",
    narration: NarrationRequest | None = None,
    provider_client: ProviderClient | None = None,
    source_revision: str | None = None,
) -> tuple[RunManifest, Path]:
    """Execute a deterministic run and return its manifest and isolated directory."""
    limits = limits or Limits()
    timestamp = datetime.now(UTC)
    run_id = f"{timestamp:%Y%m%dT%H%M%SZ}-{uuid4().hex[:12]}"
    root = output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_dir = root / run_id
    staging_dir = root / f".{run_id}.staging"
    staging_dir.mkdir(exist_ok=False)

    try:
        ingested = load_dataset(
            source,
            allowed_root=allowed_root,
            limits=limits,
            sheet_name=sheet_name,
            encoding=encoding,
        )
        result = analyze(ingested.frame, task)
        result_payload = to_dict(result)
        result_path = staging_dir / "analysis.json"
        _write_json(result_path, result_payload)
        artifacts = [_artifact(result_path, staging_dir, "analysis")]
        report_path = staging_dir / "report.html"
        write_html_report(result, report_path)
        artifacts.append(_artifact(report_path, staging_dir, "report"))

        provider = None
        provider_model = None
        if narration is not None:
            text = narrate(result, narration, client=provider_client)
            narration_path = staging_dir / "narration.txt"
            narration_path.write_text(text + "\n", encoding="utf-8")
            artifacts.append(_artifact(narration_path, staging_dir, "narration"))
            provider = narration.provider
            provider_model = narration.model

        revision, runtime_versions, dependency_versions = _execution_identity(source_revision)
        environment_path = staging_dir / "environment.json"
        _write_json(
            environment_path,
            {
                "method_version": METHOD_VERSION,
                "source_revision": revision,
                "runtime_versions": runtime_versions,
                "dependency_versions": dependency_versions,
            },
        )
        artifacts.append(_artifact(environment_path, staging_dir, "environment"))
        result_hash = _hash_json(result_payload)
        reproducibility_hash = _hash_json(
            {
                "dataset": to_dict(ingested.fingerprint),
                "task": to_dict(task),
                "method_version": METHOD_VERSION,
                "package_version": __version__,
                "source_revision": revision,
                "runtime_versions": runtime_versions,
                "dependency_versions": dependency_versions,
            }
        )
        manifest_warnings = (
            (
                "Source revision is unavailable. Set SPARK_INSIGHTS_SOURCE_REVISION to an "
                "immutable commit or build identifier for fully traceable evidence.",
            )
            if revision == "unavailable"
            else ()
        )
        manifest = RunManifest(
            schema_version="2.0",
            run_id=run_id,
            created_at_utc=timestamp.isoformat(),
            method_version=METHOD_VERSION,
            package_version=__version__,
            source_revision=revision,
            runtime_versions=runtime_versions,
            dependency_versions=dependency_versions,
            reproducibility_hash=reproducibility_hash,
            result_hash=result_hash,
            dataset=ingested.fingerprint,
            task=task,
            result=result,
            approvals={"task_confirmed": True, "cloud_transmission": narration is not None},
            manifest_warnings=manifest_warnings,
            artifacts=tuple(artifacts),
            provider=provider,
            provider_model=provider_model,
        )
        manifest_path = staging_dir / "manifest.json"
        _write_json(manifest_path, to_dict(manifest))
        staging_dir.rename(run_dir)
    except BaseException:
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise
    return replace(manifest), run_dir
