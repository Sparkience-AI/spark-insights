---
name: spark-insights-analysis
description: Profile a local CSV/XLSX dataset or run an explicitly specified Spark Insights regression/classification task with deterministic reports. Use for bounded local analysis; do not use for arbitrary code, web research, causal claims, forecasting, or autonomous target selection.
---

# Spark Insights Analysis

Use the local Spark Insights MCP tools. The server-configured dataset root and run root are hard boundaries.

## Workflow

1. Confirm the dataset relative path. Do not request or pass an absolute path or traversal.
2. For profiling, call `run_analysis_tool` with `task_type=profile` and summarize computed aggregates, warnings, and limitations.
3. For regression or classification, require the user to confirm task type, target, exclusions, missing-value policy, and whether a timestamp defines ordering. Ask for missing choices; never infer the target.
4. Call `run_analysis_tool` exactly once for the confirmed task. Report the model metric beside its baseline, split strategy, warnings, limitations, run ID, and produced artifacts.
5. Use `get_run_manifest_tool` only with a run ID returned by this server when the user asks to inspect or verify a completed run.

## Interpretation boundary

Do not turn associations into causal claims or recommendations. Do not claim forecasting, clustering, arbitrary-code analysis, web search, or autonomous model selection. A weak or baseline-losing result is evidence insufficiency, not success.

The MCP is deterministic and local-only. Do not transmit rows, values, column names, manifests, or reports to a cloud model without a separate explicit user request and application-level consent.
