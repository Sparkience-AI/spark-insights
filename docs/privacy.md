# Privacy and data flow

Local profiling, modeling, reports, and manifests require no account, API key, or network connection. Source files are read only from the user-selected allowed root. The loader reads a bounded byte snapshot once, hashes that same snapshot, and parses it without modifying the source.

The default path stores only local run artifacts under the chosen output root. It has no telemetry or background upload. API keys entered for optional narration live in memory for that process and are never written to disk.

Cloud narration is off by default. It requires a provider, editable model ID, hidden key entry, and `--consent-cloud`. The transmitted payload contains row/column counts, aggregate missing/duplicate counts, registered method, split strategy, metrics, baselines, and warning codes/messages. It excludes rows, cell values, column/target names, file paths/hashes, prompts embedded in data, and secrets. The selected provider's own retention and processing terms still apply.

Delete a run by deleting its isolated directory. Spark Insights has no remote copy to delete. Avoid publishing reports when schema names or aggregate statistics are sensitive.
