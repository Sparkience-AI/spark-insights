"""Bounded, immutable CSV/XLSX ingestion."""

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pandas as pd

from .contracts import DatasetFingerprint, Limits


class IngestionError(ValueError):
    """Raised when an input violates the explicit ingestion contract."""


class IngestedDataset:
    """Immutable-by-interface dataset snapshot."""

    def __init__(self, frame: pd.DataFrame, fingerprint: DatasetFingerprint) -> None:
        self._frame = frame.copy(deep=True)
        self.fingerprint = fingerprint

    @property
    def frame(self) -> pd.DataFrame:
        """Return a defensive deep copy for each consumer."""
        return self._frame.copy(deep=True)


def _resolve_bounded(path: Path, allowed_root: Path) -> Path:
    try:
        root = allowed_root.resolve(strict=True)
        source = path.resolve(strict=True)
    except OSError as exc:
        raise IngestionError("Allowed root and input file must exist and be accessible") from exc
    if source != root and root not in source.parents:
        raise IngestionError("Input must be inside the configured allowed root")
    if not source.is_file():
        raise IngestionError("Input must be a regular file")
    return source


def load_dataset(
    path: Path,
    *,
    allowed_root: Path,
    limits: Limits | None = None,
    sheet_name: str | None = None,
    encoding: str = "utf-8",
) -> IngestedDataset:
    """Load a bounded dataset without modifying source bytes or values."""
    limits = limits or Limits()
    source = _resolve_bounded(path, allowed_root)
    suffix = source.suffix.lower()
    if suffix not in {".csv", ".xlsx"}:
        raise IngestionError("Only CSV and XLSX files are supported")
    try:
        size = source.stat().st_size
    except OSError as exc:
        raise IngestionError("Input metadata could not be read") from exc
    if size <= 0 or size > limits.max_bytes:
        raise IngestionError(f"Input size must be between 1 and {limits.max_bytes} bytes")
    try:
        source_bytes = source.read_bytes()
    except OSError as exc:
        raise IngestionError("Input bytes could not be read") from exc
    if len(source_bytes) != size or len(source_bytes) > limits.max_bytes:
        raise IngestionError("Input changed while it was being read")
    digest = hashlib.sha256(source_bytes).hexdigest()
    selected_sheet: str | None = None

    try:
        if suffix == ".csv":
            if encoding not in {"utf-8", "utf-8-sig", "cp1252", "latin-1"}:
                raise IngestionError("CSV encoding is not allowlisted")
            frame = pd.read_csv(BytesIO(source_bytes), nrows=limits.max_rows + 1, encoding=encoding)
        else:
            from openpyxl import load_workbook

            try:
                with ZipFile(BytesIO(source_bytes)) as archive:
                    expanded = sum(info.file_size for info in archive.infolist())
                    if expanded > min(limits.max_bytes * 20, 100_000_000):
                        raise IngestionError("Workbook expanded size exceeds the safety limit")
            except BadZipFile as exc:
                raise IngestionError("XLSX input is not a valid Office archive") from exc
            workbook = load_workbook(BytesIO(source_bytes), read_only=True, data_only=False)
            try:
                if len(workbook.sheetnames) > limits.max_sheets:
                    raise IngestionError(f"Workbook exceeds {limits.max_sheets} sheets")
                selected_sheet = sheet_name or workbook.sheetnames[0]
                if selected_sheet not in workbook.sheetnames:
                    raise IngestionError("Requested worksheet does not exist")
                worksheet = workbook[selected_sheet]
                if worksheet.max_row > limits.max_rows + 1:
                    raise IngestionError(f"Dataset exceeds {limits.max_rows} rows")
                if worksheet.max_column > limits.max_columns:
                    raise IngestionError(f"Dataset exceeds {limits.max_columns} columns")
            finally:
                workbook.close()
            frame = pd.read_excel(
                BytesIO(source_bytes), sheet_name=selected_sheet, nrows=limits.max_rows + 1
            )
    except IngestionError:
        raise
    except Exception as exc:
        raise IngestionError("Input could not be parsed as the declared format") from exc

    if len(frame) > limits.max_rows:
        raise IngestionError(f"Dataset exceeds {limits.max_rows} rows")
    if len(frame.columns) > limits.max_columns:
        raise IngestionError(f"Dataset exceeds {limits.max_columns} columns")
    if frame.empty or len(frame.columns) == 0:
        raise IngestionError("Dataset must contain at least one row and column")
    if not frame.columns.is_unique:
        raise IngestionError("Duplicate column names are not supported")

    return IngestedDataset(
        frame=frame.copy(deep=True),
        fingerprint=DatasetFingerprint(
            sha256=digest,
            byte_count=size,
            format=suffix[1:],
            encoding=encoding if suffix == ".csv" else None,
            worksheet=selected_sheet,
        ),
    )
