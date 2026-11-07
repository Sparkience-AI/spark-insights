# Architecture and trust boundary

The supported flow is:

```text
bounded path inside allowed root
  -> one immutable byte snapshot + SHA-256
  -> bounded CSV/XLSX parser
  -> immutable-by-interface frame
  -> aggregate profile
  -> explicit TaskSpec
  -> registered deterministic operation
  -> baseline comparison + warnings
  -> JSON/HTML artifacts + hashed RunManifest
  -> optional aggregate-only narration after consent
```

The trusted package is `src/spark_insights`. Its supported import graph has no Smolagents, interpreter, `exec`/`eval`, shell/subprocess, browsing/search, wildcard-import, or generic network client. Provider SDKs are lazy imports used only after explicit provider/model/consent selection.

Regression uses a scikit-learn pipeline with training-fold-only preprocessing and linear regression. Classification uses the same boundary with logistic regression. A declared time column produces an ordered terminal holdout; otherwise a recorded seed controls the random holdout. Models are compared with median or majority baselines.

The historical prototype in `legacy/` and `tools/` is outside this boundary. CI scans the supported tree and launcher to prevent it from becoming reachable.

## Artifact lifecycle

Every run receives a Windows-safe UTC/UUID directory. A directory is complete only when `manifest.json` exists. Output artifacts use relative paths and hashes. The input source path is never persisted. Failed runs can leave isolated partial evidence and may be removed by the user.

## Future boundary

Custom code is not planned for the trusted process. If introduced, it requires a separately reviewed ephemeral sandbox with no default network or credentials, strict resource limits, an allowlisted package set, and scanned return artifacts.
