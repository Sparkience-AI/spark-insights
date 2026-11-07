# Evaluation and limitations

The alpha validation suite covers immutable source bytes, mutation isolation, allowed-root enforcement, format/row/column bounds, deterministic metrics, time ordering, explicit missing-value policy, baseline comparison, isolated run IDs, artifact hashes, secret/path exclusion, fake provider contracts, aggregate-only prompts, stable provider errors, launcher smoke behavior, and the supported import boundary.

Known limitations:

- Random holdout is not appropriate for grouped, panel, spatial, or repeated-subject data.
- Ordered holdout does not by itself implement rolling-origin forecasting validation.
- Accuracy can be misleading for imbalanced classification; only a deliberately small first slice is claimed.
- Linear/logistic models may underfit nonlinear data. A baseline win does not prove fitness for a decision.
- No causal, fairness, calibration, drift, or external-validity claim is made.
- Parser limits reduce risk but do not make in-process Office parsing suitable for hostile public uploads.
- AI narration can still be wrong; deterministic artifacts remain authoritative.

New analytical methods require known synthetic fixtures, leakage tests, a baseline, a metric policy, deterministic seed evidence, finite-output/property tests, explicit limitations, and independent review before being registered.
