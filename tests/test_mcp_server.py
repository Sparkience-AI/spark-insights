from __future__ import annotations

import json
from pathlib import Path

import pytest

from spark_insights.mcp_server import ServerConfig, analyze_dataset, capabilities, get_run_manifest


def _dataset(root: Path) -> None:
    (root / "data.csv").write_text(
        "feature,target\n" + "\n".join(f"{index},{index * 2}" for index in range(1, 31)) + "\n",
        encoding="utf-8",
    )


def test_mcp_profile_and_manifest_are_bounded(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    _dataset(data)
    config = ServerConfig(data, tmp_path / "runs")
    result = analyze_dataset(config, "data.csv")
    assert result["result"]["task_type"] == "profile"
    assert result["result"]["limitations"]
    manifest = get_run_manifest(config, str(result["run_id"]))
    assert manifest["run_id"] == result["run_id"]
    assert "source" not in json.dumps(manifest).lower()


def test_mcp_rejects_traversal_and_implicit_supervised_target(tmp_path: Path) -> None:
    config = ServerConfig(tmp_path, tmp_path / "runs")
    with pytest.raises(ValueError, match="relative path"):
        analyze_dataset(config, "../private.csv")
    with pytest.raises(ValueError, match="target"):
        analyze_dataset(config, "data.csv", task_type="regression")
    assert "arbitrary code" in capabilities()["unsupported"]


def test_mcp_rejects_oversized_arguments(tmp_path: Path) -> None:
    config = ServerConfig(tmp_path, tmp_path / "runs")
    with pytest.raises(ValueError, match="1024-character"):
        analyze_dataset(config, "x" * 1025)
    with pytest.raises(ValueError, match="250-item"):
        analyze_dataset(config, "data.csv", exclusions=["x"] * 251)
    with pytest.raises(ValueError, match="256-character"):
        analyze_dataset(config, "data.csv", units="x" * 257)
    with pytest.raises(ValueError, match="32-bit"):
        analyze_dataset(config, "data.csv", seed=2**31)


def test_mcp_supervised_result_keeps_baseline_and_limitations(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    _dataset(data)
    result = analyze_dataset(
        ServerConfig(data, tmp_path / "runs"), "data.csv", "regression", "target"
    )
    metric = result["result"]["metrics"][0]
    assert metric["baseline_value"] >= 0
    assert result["result"]["limitations"]


def test_skill_package_has_negative_routing_evals() -> None:
    root = Path(__file__).parents[1] / ".agents" / "skills" / "spark-insights-analysis"
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    cases = json.loads((root / "evals" / "cases.json").read_text(encoding="utf-8"))["cases"]
    assert "TODO" not in skill
    assert any(case["should_trigger"] is False for case in cases)
    assert any("no autonomous target selection" in case["expected"] for case in cases)
