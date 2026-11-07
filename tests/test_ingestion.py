from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from spark_insights.contracts import Limits
from spark_insights.ingestion import IngestionError, load_dataset


def test_ingestion_preserves_bytes_and_values(tmp_path: Path) -> None:
    source = tmp_path / "data.csv"
    source.write_text("a,b\n1,x\n, y\n", encoding="utf-8")
    before = source.read_bytes()
    loaded = load_dataset(source, allowed_root=tmp_path)
    assert source.read_bytes() == before
    assert pd.isna(loaded.frame.loc[1, "a"])
    assert loaded.frame.loc[1, "b"] == " y"
    mutated = loaded.frame
    mutated.loc[0, "a"] = 999
    assert loaded.frame.loc[0, "a"] == 1
    assert len(loaded.fingerprint.sha256) == 64


def test_ingestion_rejects_outside_root_and_limits(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.csv"
    outside.write_text("a\n1\n", encoding="utf-8")
    with pytest.raises(IngestionError, match="allowed root"):
        load_dataset(outside, allowed_root=allowed)

    inside = allowed / "wide.csv"
    inside.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(IngestionError, match="columns"):
        load_dataset(inside, allowed_root=allowed, limits=Limits(max_columns=1))


def test_only_csv_and_xlsx_are_supported(tmp_path: Path) -> None:
    source = tmp_path / "data.xls"
    source.write_bytes(b"not-a-workbook")
    with pytest.raises(IngestionError, match="CSV and XLSX"):
        load_dataset(source, allowed_root=tmp_path)


def test_missing_root_and_input_are_controlled_errors(tmp_path: Path) -> None:
    with pytest.raises(IngestionError, match="must exist"):
        load_dataset(tmp_path / "missing.csv", allowed_root=tmp_path)
    with pytest.raises(IngestionError, match="must exist"):
        load_dataset(tmp_path / "missing.csv", allowed_root=tmp_path / "missing-root")
