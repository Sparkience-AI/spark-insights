#!/usr/bin/env python3
"""Compatibility launcher for the supported deterministic CLI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def _main() -> int:
    from spark_insights.cli import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
