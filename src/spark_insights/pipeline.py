"""Trusted orchestration plane for one isolated analysis run."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from . import __version__
from .analysis import analyze
from .contracts import ArtifactRecord, Limits, RunManifest, TaskSpec, to_dict
from .ingestion import load_dataset
from .providers import NarrationRequest, ProviderClient, narrate
from .reporting import write_html_report


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
) -> tuple[RunManifest, Path]:
    """Execute a deterministic run and return its manifest and isolated directory."""
    limits = limits or Limits()
    timestamp = datetime.now(UTC)
    run_id = f"{timestamp:%Y%m%dT%H%M%SZ}-{uuid4().hex[:12]}"
    root = output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_dir = root / run_id
    run_dir.mkdir(exist_ok=False)

    ingested = load_dataset(
        source,
        allowed_root=allowed_root,
        limits=limits,
        sheet_name=sheet_name,
        encoding=encoding,
    )
    result = analyze(ingested.frame, task)
    result_path = run_dir / "analysis.json"
    _write_json(result_path, to_dict(result))
    artifacts = [_artifact(result_path, run_dir, "analysis")]
    report_path = run_dir / "report.html"
    write_html_report(result, report_path)
    artifacts.append(_artifact(report_path, run_dir, "report"))

    provider = None
    provider_model = None
    if narration is not None:
        text = narrate(result, narration, client=provider_client)
        narration_path = run_dir / "narration.txt"
        narration_path.write_text(text + "\n", encoding="utf-8")
        artifacts.append(_artifact(narration_path, run_dir, "narration"))
        provider = narration.provider
        provider_model = narration.model

    environment_path = run_dir / "environment.json"
    _write_json(
        environment_path,
        {
            "python": platform.python_version(),
            "implementation": sys.implementation.name,
            "spark_insights": __version__,
        },
    )
    artifacts.append(_artifact(environment_path, run_dir, "environment"))
    manifest = RunManifest(
        schema_version="1.0",
        run_id=run_id,
        created_at_utc=timestamp.isoformat(),
        package_version=__version__,
        dataset=ingested.fingerprint,
        task=task,
        result=result,
        approvals={"task_confirmed": True, "cloud_transmission": narration is not None},
        artifacts=tuple(artifacts),
        provider=provider,
        provider_model=provider_model,
    )
    manifest_path = run_dir / "manifest.json"
    _write_json(manifest_path, to_dict(manifest))
    return replace(manifest), run_dir
