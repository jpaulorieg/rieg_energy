# Changelog

## 0.4.2

- Migrated the PostgreSQL integration from `asyncpg` to `psycopg3` for Home Assistant compatibility.
- Switched the integration dependency from `asyncpg==0.30.0` to `psycopg[binary]>=3.2`.
- Updated the API client to use `psycopg.AsyncConnection` and `AsyncCursor` with async query execution and dict-based row access.
- Refreshed the documentation and test coverage for the new driver.

## 0.4.1

- Removed compiled Python artifacts from the repository.
- Added `CONTRIBUTING.md` with coding, git, commit, pull request, testing, and development environment guidance.
- Added `docs/installation.md`, `docs/postgres.md`, `docs/statistics.md`, `docs/dashboard.md`, `docs/development.md`, and `docs/faq.md`.
- Added GitHub workflows for `release` and `hassfest`.
- Updated CI to type-check `tests` and prepared the project for `pytest-cov`.
- Corrected invalid development dependency pins and aligned the repository with a real Home Assistant package baseline available for validation.
- Updated the integration version to `0.4.1`.
- Fixed irradiance sensor units to use ASCII-safe values.
- Expanded the automated tests with additional coverage for API helpers, config flow, coordinator diagnostics, sensor date handling, and statistics helpers.
- Rewrote the README with badges, compatibility information, entity documentation, service documentation, screenshots placeholders, and links to the docs folder.
- Tightened the roadmap so only genuinely implemented functionality remains checked.
- Added `AUDIT_REPORT.md` to summarize findings, fixes, risks, and next steps.
