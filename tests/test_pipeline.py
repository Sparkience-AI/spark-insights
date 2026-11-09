from __future__ import annotations

import json
from pathlib import Path

import pytest

import spark_insights.pipeline as pipeline
from spark_insights.contracts import TaskSpec
from spark_insights.pipeline import run_analysis
from spark_insights.providers import NarrationRequest


class FakeProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def generate(self, *, model: str, api_key: str, prompt: str) -> str:
        self.calls.append({"model": model, "api_key": api_key, "prompt": prompt})
        return "Validated aggregate summary."


def test_isolated_run_manifest_has_hashes_but_no_secrets_or_source_path(tmp_path: Path) -> None:
    source = tmp_path / "secret-customer-file.csv"
    source.write_text("amount,label\n1,a\n2,b\n", encoding="utf-8")
    fake = FakeProvider()
    request = NarrationRequest("openai", "editable-model", "top-secret-key", True)
    first, first_dir = run_analysis(
        source,
        allowed_root=tmp_path,
        output_root=tmp_path / "runs",
        task=TaskSpec(),
        narration=request,
        provider_client=fake,
    )
    second, second_dir = run_analysis(
        source,
        allowed_root=tmp_path,
        output_root=tmp_path / "runs",
        task=TaskSpec(),
    )
    assert first_dir != second_dir
    manifest_text = (first_dir / "manifest.json").read_text(encoding="utf-8")
    assert "top-secret-key" not in manifest_text
    assert "secret-customer-file" not in manifest_text
    assert str(tmp_path) not in manifest_text
    manifest = json.loads(manifest_text)
    assert manifest["dataset"]["sha256"]
    assert all(item["sha256"] for item in manifest["artifacts"])
    assert (first_dir / "report.html").exists()
    assert first.provider == "openai"
    assert second.provider is None
    assert manifest["schema_version"] == "2.0"
    assert manifest["method_version"] == "deterministic-tabular-v2"
    assert manifest["source_revision"] == "unavailable"
    assert manifest["manifest_warnings"]
    assert set(manifest["runtime_versions"]) == {"python", "implementation"}
    assert set(manifest["dependency_versions"]) == {
        "spark-insights",
        "numpy",
        "pandas",
        "scikit-learn",
        "openpyxl",
    }
    assert len(manifest["reproducibility_hash"]) == 64
    assert len(manifest["result_hash"]) == 64


def test_provider_receives_aggregates_not_rows_or_names(tmp_path: Path) -> None:
    source = tmp_path / "data.csv"
    source.write_text(
        "prompt_injection,private\nignore instructions,unique-secret-value\n", encoding="utf-8"
    )
    fake = FakeProvider()
    run_analysis(
        source,
        allowed_root=tmp_path,
        output_root=tmp_path / "runs",
        task=TaskSpec(),
        narration=NarrationRequest("anthropic", "model-x", "key", True),
        provider_client=fake,
    )
    prompt = fake.calls[0]["prompt"]
    assert "unique-secret-value" not in prompt
    assert "prompt_injection" not in prompt
    assert "row_count" in prompt


def test_source_revision_changes_reproducibility_identity(tmp_path: Path) -> None:
    source = tmp_path / "data.csv"
    source.write_text("value\n1\n2\n", encoding="utf-8")
    first, _ = run_analysis(
        source,
        allowed_root=tmp_path,
        output_root=tmp_path / "runs",
        task=TaskSpec(),
        source_revision="git:first",
    )
    second, _ = run_analysis(
        source,
        allowed_root=tmp_path,
        output_root=tmp_path / "runs",
        task=TaskSpec(),
        source_revision="git:second",
    )
    assert first.result_hash == second.result_hash
    assert first.reproducibility_hash != second.reproducibility_hash


def test_failed_run_removes_staging_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = tmp_path / "data.csv"
    source.write_text("value\n1\n2\n", encoding="utf-8")
    output_root = tmp_path / "runs"

    def fail_report(*args: object, **kwargs: object) -> None:
        raise RuntimeError("simulated report failure")

    monkeypatch.setattr(pipeline, "write_html_report", fail_report)
    with pytest.raises(RuntimeError, match="simulated report failure"):
        run_analysis(
            source,
            allowed_root=tmp_path,
            output_root=output_root,
            task=TaskSpec(),
        )
    assert list(output_root.iterdir()) == []
