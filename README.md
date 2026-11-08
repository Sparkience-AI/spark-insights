# Spark Insights

Spark Insights is a local-first, reproducible assisted data-analysis tool for CSV and XLSX files. It profiles data, runs an explicitly selected regression or classification baseline workflow, compares the result with a simple baseline, and produces machine-readable and portable HTML reports.

**Status: alpha.** The deterministic profiling and supervised-analysis slice is supported. It is not an autonomous data scientist, a causal inference system, or a substitute for expert review.

## Why it is different

- Your dataset stays local unless you explicitly choose cloud narration.
- The supported path never executes model-authored code, invokes a shell, browses the web, or silently cleans data.
- Inputs are read once, hashed, bounded, and kept immutable by interface.
- Tasks, targets, exclusions, time semantics, missing-value policy, seed, and holdout are explicit.
- Preprocessing is fitted only on training data. Every model metric is shown beside a deterministic baseline.
- Each run has a collision-safe directory, typed JSON result, portable HTML report, environment record, and manifest with artifact hashes.
- Optional Gemini, OpenAI, or Anthropic narration receives only bounded aggregates—never rows, values, column names, file paths, or credentials.

## Install and run

Spark Insights supports Python 3.11–3.13.

```bash
git clone https://github.com/Sparkience-AI/spark-insights.git
cd spark-insights
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
python main.py datasets/sales.csv --allowed-root datasets --encoding cp1252
```

Supervised regression example:

```bash
python main.py datasets/sales.csv --allowed-root datasets --encoding cp1252 --task regression --target SALES --exclude ORDERNUMBER --seed 42
```

If a timestamp column defines ordering, add `--time-column ORDERDATE`. Invalid timestamps are rejected; Spark Insights never invents time semantics. Missing features are rejected by default. To explicitly permit training-fold-only median/mode imputation, add `--missing-policy train_median_mode`.

Run `python main.py --help` for the stable option and resource-limit contract. Exit codes are 0 (success), 2 (input/argument), 3 (analysis), 4 (provider), and 10 (internal failure).

## Local MCP and agent skill

Set `SPARK_INSIGHTS_ALLOWED_ROOT` to the approved dataset directory and optionally `SPARK_INSIGHTS_OUTPUT_ROOT` to an artifact directory, then run `spark-insights-mcp`. The local stdio server exposes capability discovery, explicit profile/regression/classification runs, and completed-manifest retrieval. Tool callers cannot override the roots, pass absolute/traversing paths, invoke the legacy agent, execute code, browse, or trigger cloud narration.

The repo-local `spark-insights-analysis` skill under `.agents/skills/` teaches compatible agents to confirm the task and target, compare every metric with its baseline, preserve limitations, and reject unsupported requests.

## Optional cloud narration (BYOK)

Install providers:

```bash
python -m pip install -e ".[providers]"
```

Then choose a provider and any model ID:

```bash
python main.py datasets/sales.csv --allowed-root datasets --encoding cp1252 --provider openai --model YOUR_MODEL_ID --consent-cloud
```

The key is requested through a hidden prompt and retained only in process memory. It is not read from or written to `.env`, reports, logs, or manifests. `--consent-cloud` is mandatory. OpenAI requests use the Responses API with storage disabled. Cloud narration is advisory and cannot change calculations.

## Output contract

Each successful run creates `runs/<UTC timestamp>-<random suffix>/` containing:

- `analysis.json` — typed computed aggregates, metrics, warnings, and limitations;
- `report.html` — self-contained deterministic report and metric comparison visualization;
- `environment.json` — local runtime identity; and
- `manifest.json` — input hash/size/format, confirmed task, seed, approvals, versions, and artifact hashes.

The manifest contains no source path, dataset rows, API key, prompt, or narration input. A rejected/failed run may leave an empty or partial isolated directory; it is never treated as complete without `manifest.json`.

## Supported scope and limitations

Supported now:

- bounded CSV and modern XLSX ingestion;
- aggregate schema/data-quality profiling;
- explicit linear regression and logistic classification;
- seeded random holdout or explicitly ordered time holdout;
- median/majority baselines, MAE/accuracy, warnings, JSON and HTML reports;
- aggregate-only optional narration using Gemini, OpenAI, or Anthropic.

Not supported yet:

- causal claims, forecasting, clustering, arbitrary/custom code, web search, autonomous task/target selection;
- production deployment, multi-user hosting, model persistence, arbitrary filesystem access;
- the prototype's auto-generated PowerPoint and open-ended chart generation. These remain historical demo artifacts, not supported outputs.

XLSX archives have compressed, expanded-size, sheet, row, and column guards. Office parsing still occurs in-process; do not use the alpha release as an adversarial public upload service.

## Architecture, privacy, and evaluation

- [Architecture and trust boundary](docs/architecture.md)
- [Privacy and data flow](docs/privacy.md)
- [Evaluation and limitations](docs/evaluation.md)
- [Threat model](docs/threat-model.md)
- [Release readiness](docs/release-readiness.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

The former unrestricted Smolagents implementation is isolated under `legacy/` and `tools/`. It is retained only for historical comparison, is not installed, and is never imported by `main.py` or the `spark_insights` package. Do not use it with sensitive or untrusted data.

## Development

```bash
uv sync --group dev --extra providers
.venv/Scripts/python -m pytest  # Windows
.venv/Scripts/ruff check .
.venv/Scripts/mypy src
.venv/Scripts/python -m build
```

The authoritative dependencies are in `pyproject.toml`; `uv.lock` makes clean resolution reproducible. Contributions must preserve deterministic local operation with zero API keys and zero network access.

## License

MIT. See [LICENSE](LICENSE).
