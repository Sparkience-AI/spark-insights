# Threat model

## Assets and trust boundary

Spark Insights protects local dataset bytes, explicit task choices, deterministic metrics, isolated artifacts, manifests, and optional provider keys. The trusted Python package and local stdio MCP process are inside the boundary. Dataset cells, filenames, MCP arguments, provider output, and legacy prototype files are untrusted.

## Primary threats and controls

- **Arbitrary execution or network access:** the supported package and MCP import graph excludes
  `legacy/`, `exec`, shells, subprocesses, and web search. Historical dynamic helpers are quarantined
  below `legacy/unrestricted_tools/` rather than exposed as a root import package.
- **Filesystem escape:** the server fixes one allowed dataset root and one output root at startup. Tool calls accept only bounded relative non-traversing paths; ingestion resolves symlinks inside the data root, and manifest retrieval resolves symlinks inside the output root and accepts only generated run IDs.
- **Silent mutation or leakage:** source bytes are read once, hashed, parsed from the same buffer, and exposed through defensive frame copies. Transform policy, task, seed, and approvals are recorded.
- **Partial evidence:** artifacts are written to a unique staging directory, the manifest is written
  last, and the directory is atomically committed. Failures remove only that run's staging directory.
- **Spreadsheet exhaustion:** compressed/expanded byte, sheet, row, and column limits are enforced before analysis. Office parsing remains in-process and is not a public hostile-upload sandbox.
- **Analytical overclaim:** supervised targets are mandatory, preprocessing fits training data only, metrics include simple baselines, and results carry warnings and fixed method limitations.
- **Prompt injection and credentials:** MCP performs no provider calls. Cells are data, never instructions or code. Optional CLI narration is separately consent-gated and aggregate-only.

## Residual risk

The process inherits the invoking user's OS permissions. A malicious parser exploit could exceed application controls; use trusted local datasets. Statistical associations are not causal conclusions or professional advice.
