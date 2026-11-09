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

The historical prototype, including its dynamic execution helpers, is quarantined entirely under
`legacy/`. CI scans the supported tree and launcher to prevent it from becoming reachable.

## Artifact lifecycle

Every run is assembled in a Windows-safe UTC/UUID staging directory and atomically renamed only
after `manifest.json` is complete. Output artifacts use relative paths and hashes. The input source
path is never persisted. Failed runs attempt to remove their exact staging directory. If an OS lock
or permission error blocks cleanup, only the hidden `.staging` directory can remain; it is never
presented as a completed run.

## Future boundary

Custom code is not planned for the trusted process. If introduced, it requires a separately reviewed ephemeral sandbox with no default network or credentials, strict resource limits, an allowlisted package set, and scanned return artifacts.
