from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


def test_supported_package_has_no_unsafe_execution_or_agent_imports() -> None:
    package = Path("src/spark_insights")
    forbidden_calls = {"exec", "eval", "compile", "__import__"}
    forbidden_roots = {"subprocess", "smolagents", "requests", "httpx"}
    forbidden_attributes = {"exec", "eval", "system", "popen", "run", "call", "check_output"}
    for path in package.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls, f"{path}: {node.func.id}"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_attributes, f"{path}: {node.func.attr}"
            if isinstance(node, ast.Import):
                assert not ({alias.name.split(".")[0] for alias in node.names} & forbidden_roots)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden_roots


def test_compatibility_launcher_only_imports_supported_cli() -> None:
    tree = ast.parse(Path("main.py").read_text(encoding="utf-8"))
    imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert "spark_insights.cli" in imports
    assert "agent" not in imports


def test_clean_checkout_help_command() -> None:
    completed = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "Reproducible local-first" in completed.stdout
