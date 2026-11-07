"""Local stdio MCP adapter for Spark Insights' trusted deterministic pipeline."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import Any, Literal

from .contracts import Limits, TaskSpec, to_dict
from .pipeline import run_analysis

_RUN_ID = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{12}$")
MAX_MCP_PATH_CHARS = 1024
MAX_MCP_TEXT_CHARS = 256
MAX_MCP_EXCLUSIONS = 250
MAX_MANIFEST_BYTES = 25_000_000


@dataclass(frozen=True)
class ServerConfig:
    allowed_root: Path
    output_root: Path
    limits: Limits = field(default_factory=Limits)

    @classmethod
    def from_environment(cls) -> ServerConfig:
        source = os.environ.get("SPARK_INSIGHTS_ALLOWED_ROOT")
        if not source:
            raise RuntimeError(
                "SPARK_INSIGHTS_ALLOWED_ROOT must identify the approved dataset directory."
            )
        root = Path(source).resolve(strict=True)
        if not root.is_dir():
            raise RuntimeError("SPARK_INSIGHTS_ALLOWED_ROOT must be a directory.")
        output = Path(os.environ.get("SPARK_INSIGHTS_OUTPUT_ROOT", root / "runs")).resolve()
        return cls(allowed_root=root, output_root=output)


def capabilities() -> dict[str, object]:
    return {
        "product": "Spark Insights",
        "transport": "local stdio",
        "tasks": ["profile", "regression", "classification"],
        "requires_cloud": False,
        "requires_explicit_target": ["regression", "classification"],
        "unsupported": [
            "arbitrary code",
            "web search",
            "causal inference",
            "forecasting",
            "autonomous task selection",
        ],
    }


def _relative_source(config: ServerConfig, relative_path: str) -> Path:
    if len(relative_path) > MAX_MCP_PATH_CHARS:
        raise ValueError(f"Dataset path exceeds the {MAX_MCP_PATH_CHARS}-character limit.")
    candidate = PurePath(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise ValueError("Dataset path must be a non-empty relative path without traversal.")
    return config.allowed_root.joinpath(*candidate.parts)


def _validate_text(value: str | None, field_name: str) -> None:
    if value is not None and len(value) > MAX_MCP_TEXT_CHARS:
        raise ValueError(f"{field_name} exceeds the {MAX_MCP_TEXT_CHARS}-character limit.")


def analyze_dataset(
    config: ServerConfig,
    relative_path: str,
    task_type: Literal["profile", "regression", "classification"] = "profile",
    target: str | None = None,
    exclusions: list[str] | None = None,
    time_column: str | None = None,
    units: str | None = None,
    seed: int = 42,
    test_fraction: float = 0.2,
    missing_policy: Literal["reject", "train_median_mode"] = "reject",
    sheet_name: str | None = None,
    encoding: Literal["utf-8", "utf-8-sig", "cp1252", "latin-1"] = "utf-8",
) -> dict[str, object]:
    """Run one explicit deterministic task inside the configured roots."""
    if task_type != "profile" and not target:
        raise ValueError("A target is required for supervised tasks.")
    for value, field_name in (
        (target, "Target"),
        (time_column, "Time column"),
        (units, "Units"),
        (sheet_name, "Sheet name"),
    ):
        _validate_text(value, field_name)
    selected_exclusions = exclusions or []
    if len(selected_exclusions) > MAX_MCP_EXCLUSIONS:
        raise ValueError(f"Exclusions exceed the {MAX_MCP_EXCLUSIONS}-item limit.")
    for exclusion in selected_exclusions:
        _validate_text(exclusion, "Exclusion")
    if not -(2**31) <= seed < 2**31:
        raise ValueError("Seed must be a signed 32-bit integer.")
    manifest, run_dir = run_analysis(
        _relative_source(config, relative_path),
        allowed_root=config.allowed_root,
        output_root=config.output_root,
        task=TaskSpec(
            task_type=task_type,
            target=target,
            exclusions=tuple(selected_exclusions),
            time_column=time_column,
            units=units,
            seed=seed,
            test_fraction=test_fraction,
            missing_policy=missing_policy,
        ),
        limits=config.limits,
        sheet_name=sheet_name,
        encoding=encoding,
    )
    return {
        "run_id": manifest.run_id,
        "result": to_dict(manifest.result),
        "artifacts": [to_dict(item) for item in manifest.artifacts],
        "run_directory": run_dir.relative_to(config.output_root).as_posix(),
    }


def get_run_manifest(config: ServerConfig, run_id: str) -> dict[str, object]:
    """Read one completed manifest without accepting an arbitrary path."""
    if not _RUN_ID.fullmatch(run_id):
        raise ValueError("Run ID has an invalid format.")
    try:
        root = config.output_root.resolve(strict=True)
        manifest_path = (root / run_id / "manifest.json").resolve(strict=True)
        if root not in manifest_path.parents or not manifest_path.is_file():
            raise ValueError("Completed run manifest escaped the configured output root.")
        if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
            raise ValueError("Completed run manifest exceeds the response limit.")
        payload = manifest_path.read_text(encoding="utf-8")
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError("Completed run manifest was not found.") from exc
    value = json.loads(payload)
    if not isinstance(value, dict) or value.get("run_id") != run_id:
        raise ValueError("Run manifest is invalid.")
    return value


def build_server(config: ServerConfig | None = None) -> Any:
    from mcp.server.fastmcp import FastMCP

    active = config or ServerConfig.from_environment()
    server = FastMCP(
        "Spark Insights",
        instructions=(
            "Use only for explicit local profiling, regression, or classification. "
            "Never choose a supervised target without user confirmation or infer causal "
            "conclusions."
        ),
    )
    server.tool()(capabilities)

    @server.tool()
    def run_analysis_tool(
        relative_path: str,
        task_type: Literal["profile", "regression", "classification"] = "profile",
        target: str | None = None,
        exclusions: list[str] | None = None,
        time_column: str | None = None,
        units: str | None = None,
        seed: int = 42,
        test_fraction: float = 0.2,
        missing_policy: Literal["reject", "train_median_mode"] = "reject",
        sheet_name: str | None = None,
        encoding: Literal["utf-8", "utf-8-sig", "cp1252", "latin-1"] = "utf-8",
    ) -> dict[str, object]:
        return analyze_dataset(
            active,
            relative_path,
            task_type,
            target,
            exclusions,
            time_column,
            units,
            seed,
            test_fraction,
            missing_policy,
            sheet_name,
            encoding,
        )

    @server.tool()
    def get_run_manifest_tool(run_id: str) -> dict[str, object]:
        return get_run_manifest(active, run_id)

    return server


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
