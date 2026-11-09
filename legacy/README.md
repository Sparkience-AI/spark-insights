# Unsupported legacy prototype

These files document the original unrestricted Smolagents prototype. They are not installed, imported, tested as product behavior, or safe for sensitive/untrusted data. The original agent combined model-directed code execution, wildcard imports, filesystem access, and external search. It is retained only to make the migration auditable.

Historical dynamic helpers are quarantined in `legacy/unrestricted_tools/` so they are not exposed
as a root `tools` import package. The supported application is `main.py` backed solely by
`src/spark_insights`.

The original import statements are preserved as historical evidence and intentionally no longer
resolve from the repository root.
