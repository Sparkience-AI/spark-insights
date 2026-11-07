# Contributing

Open an issue before adding an analytical method or changing a metric contract. Contributions must keep the default path local, deterministic, and usable without an API key or network.

1. Create a branch and install `uv sync --extra dev --extra providers`.
2. Add tests for behavior, limits, privacy, deterministic replay, leakage, baselines, and failure modes.
3. Run pytest, Ruff, mypy, and a package build.
4. Update README, architecture/privacy/evaluation documentation, and `llms.txt` when the public contract changes.
5. Open a focused pull request. Never commit datasets containing personal/confidential data, keys, generated run directories, or provider responses.

New analytical methods need an explicit typed specification, accepted inputs/units, deterministic seed policy, known synthetic fixtures, a simple baseline, metric acceptance policy, limitations, and independent review. Model-authored code execution, shell access, browsing, or hidden preprocessing will not be accepted into the trusted package.
