# Contributing

## Code Standard

- Use Python with full type hints.
- Follow official Home Assistant integration patterns.
- Prefer `async`/`await` for all I/O and PostgreSQL access.
- Format code with `black` and lint with `ruff`.
- Keep entities, coordinators, services, and persistence concerns separated.
- Do not write directly to the Home Assistant database.

## Development Environment

1. Create a virtual environment with Python 3.13.
2. Activate it.
3. Install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Running Tests

Run the full validation suite before opening a pull request:

```bash
black .
ruff check .
mypy custom_components tests
pytest
```

Coverage target:

- Minimum `95%` for `custom_components/rieg_energy`

## Git Flow

- Branch from `main`.
- Use short-lived branches for each change.
- Prefer branch names like:
  - `feat/...`
  - `fix/...`
  - `docs/...`
  - `chore/...`
- Rebase or merge `main` before opening the pull request if the branch diverged.

## Commit Convention

Use Conventional Commits:

- `feat: add statistics rebuild workflow`
- `fix: handle empty monthly history import`
- `docs: expand PostgreSQL setup guide`
- `test: add coordinator diagnostics coverage`
- `chore: update development dependencies`

## Pull Request Policy

- Keep pull requests focused on a single concern.
- Include tests for behavioral changes.
- Update documentation when features, services, entities, or setup steps change.
- Do not mix unrelated refactors with feature work.
- Ensure CI, Hassfest, linting, typing, tests, and coverage all pass.

## Home Assistant Specific Rules

- Use only official Home Assistant APIs.
- Use `DataUpdateCoordinator` for data refresh orchestration.
- Use `Config Flow` for setup.
- Keep sensor properties pure and memory-backed.
- Prefer diagnostics and storage helpers over ad hoc files or recorder writes.
