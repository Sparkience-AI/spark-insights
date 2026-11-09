# Security policy

Please do not open public issues for suspected vulnerabilities or include secrets, personal data, or exploit datasets in reports. Use GitHub's private vulnerability reporting for this repository. If that option is unavailable, contact the maintainers through the security channel listed on the Sparkience AI organization profile.

The supported surface is `src/spark_insights` and `main.py`. Files under `legacy/` are explicitly
unsupported historical prototype code; dynamic helpers are quarantined under
`legacy/unrestricted_tools/` and are not installed. Security fixes target the latest `main`; no
long-term support versions are currently promised while the project is alpha.

Include the affected commit, operating system/Python version, impact, and a minimal non-sensitive reproduction. Maintainers will acknowledge a valid private report, assess severity, coordinate a fix, and publish credit/advisory details with the reporter's consent.
