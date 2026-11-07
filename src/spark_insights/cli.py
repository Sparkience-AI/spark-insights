"""Stable command-line interface for the trusted deterministic path."""

from __future__ import annotations

import argparse
import getpass
import sys
from collections.abc import Sequence
from pathlib import Path

from .analysis import AnalysisError
from .contracts import Limits, TaskSpec
from .ingestion import IngestionError
from .pipeline import run_analysis
from .providers import NarrationRequest, ProviderError

EXIT_OK = 0
EXIT_INPUT = 2
EXIT_ANALYSIS = 3
EXIT_PROVIDER = 4
EXIT_INTERNAL = 10


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spark-insights",
        description="Reproducible local-first profiling and supervised analysis.",
    )
    parser.add_argument("input", type=Path, help="CSV or XLSX file inside --allowed-root")
    parser.add_argument("--allowed-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=Path("runs"))
    parser.add_argument("--sheet", help="XLSX worksheet name; defaults to the first sheet")
    parser.add_argument(
        "--encoding",
        choices=("utf-8", "utf-8-sig", "cp1252", "latin-1"),
        default="utf-8",
        help="Explicit CSV text encoding",
    )
    parser.add_argument(
        "--task", choices=("profile", "regression", "classification"), default="profile"
    )
    parser.add_argument("--target", help="Required for regression or classification")
    parser.add_argument(
        "--exclude", action="append", default=[], help="Feature to exclude; repeatable"
    )
    parser.add_argument("--time-column", help="Use ordered holdout based on this timestamp column")
    parser.add_argument("--units", help="Optional target units recorded in the manifest")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument(
        "--missing-policy", choices=("reject", "train_median_mode"), default="reject"
    )
    parser.add_argument("--max-bytes", type=int, default=20_000_000)
    parser.add_argument("--max-rows", type=int, default=100_000)
    parser.add_argument("--max-columns", type=int, default=250)
    parser.add_argument("--max-sheets", type=int, default=10)
    parser.add_argument("--provider", choices=("gemini", "openai", "anthropic"))
    parser.add_argument("--model", help="Editable provider model ID")
    parser.add_argument(
        "--consent-cloud",
        action="store_true",
        help="Confirm aggregate result transmission to the chosen provider",
    )
    return parser


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.task != "profile" and not args.target:
        parser.error("--target is required for supervised tasks")
    if args.provider and not args.model:
        parser.error("--model is required when --provider is selected")
    if args.provider and not args.consent_cloud:
        parser.error("--consent-cloud is required when --provider is selected")
    if (args.model or args.consent_cloud) and not args.provider:
        parser.error("--provider is required for cloud narration")
    if min(args.max_bytes, args.max_rows, args.max_columns, args.max_sheets) <= 0:
        parser.error("resource limits must be positive")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate_args(parser, args)
    narration = None
    if args.provider:
        key = getpass.getpass(f"{args.provider} API key (session only): ")
        narration = NarrationRequest(
            provider=args.provider,
            model=args.model,
            api_key=key,
            consent=args.consent_cloud,
        )
    try:
        manifest, run_dir = run_analysis(
            args.input,
            allowed_root=args.allowed_root,
            output_root=args.output_root,
            task=TaskSpec(
                task_type=args.task,
                target=args.target,
                exclusions=tuple(args.exclude),
                time_column=args.time_column,
                units=args.units,
                seed=args.seed,
                test_fraction=args.test_fraction,
                missing_policy=args.missing_policy,
            ),
            limits=Limits(args.max_bytes, args.max_rows, args.max_columns, args.max_sheets),
            sheet_name=args.sheet,
            encoding=args.encoding,
            narration=narration,
        )
    except IngestionError as exc:
        print(f"Input rejected: {exc}", file=sys.stderr)
        return EXIT_INPUT
    except AnalysisError as exc:
        print(f"Analysis rejected: {exc}", file=sys.stderr)
        return EXIT_ANALYSIS
    except ProviderError:
        print("Provider failed: cloud narration request failed", file=sys.stderr)
        return EXIT_PROVIDER
    except (ImportError, RuntimeError, ValueError) as exc:
        print(f"Run failed: {exc}", file=sys.stderr)
        return EXIT_INTERNAL
    print(f"Run complete: {manifest.run_id}")
    print(f"Artifacts: {run_dir}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
