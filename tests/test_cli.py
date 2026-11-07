from __future__ import annotations

from pathlib import Path

from spark_insights import cli
from spark_insights.providers import ProviderError


def test_provider_failure_uses_stable_exit_and_message(monkeypatch, capsys, tmp_path: Path) -> None:
    source = tmp_path / "data.csv"
    source.write_text("x\n1\n", encoding="utf-8")
    monkeypatch.setattr(cli.getpass, "getpass", lambda _: "secret-key")

    def fail(*args, **kwargs):
        raise ProviderError("private SDK/account detail")

    monkeypatch.setattr(cli, "run_analysis", fail)
    code = cli.main(
        [
            str(source),
            "--allowed-root",
            str(tmp_path),
            "--provider",
            "openai",
            "--model",
            "editable",
            "--consent-cloud",
        ]
    )
    captured = capsys.readouterr()
    assert code == cli.EXIT_PROVIDER
    assert captured.err.strip() == "Provider failed: cloud narration request failed"
    assert "secret-key" not in captured.err
    assert "private" not in captured.err
