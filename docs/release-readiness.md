# Release readiness

## Verification gates

- Tests, Ruff, strict mypy, locked resolution, source/wheel build, installed CLI/MCP smoke checks, and documentation discovery pass.
- Adversarial fixtures cover traversal and symlink containment, bounded MCP arguments/manifests,
  malformed archives, expansion limits, missing targets, prompt-like cell content, provider failures,
  legacy import isolation, atomic failure cleanup, and run-manifest identity/integrity.
- Skill evals include positive routing, missing-input questions, unsupported arbitrary-code requests, and traversal refusal.
- HTML output has semantic headings, tables, visible metric labels in addition to color, responsive viewport metadata, escaped values, and a keyboard/manual screen-reader spot check before a tagged release.

## Performance envelope

Default limits are 20 MB, 100,000 rows, 250 columns, and 10 XLSX sheets. The release target is under 10 seconds for a 10,000-row profile and under 30 seconds for the reference supervised fixture on a typical developer laptop. CI avoids brittle hardware timing thresholds while retaining bounded golden fixtures.

## Release and rollback

The manual release-evidence workflow creates Python source/wheel artifacts, a CycloneDX SBOM, SHA-256 checksums, and provenance attestations. It creates no installer. Validate artifacts in a clean virtual environment and publish limitations with the tag. Roll back by withdrawing the affected release and returning to the previous verified artifacts; isolated run directories remain user-controlled and are never deleted automatically.
