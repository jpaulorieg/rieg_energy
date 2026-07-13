# Development

## Tooling

- Python 3.13
- Home Assistant Core
- `psycopg3`
- `pytest`
- `pytest-cov`
- `ruff`
- `black`
- `mypy`

## Useful Commands

```bash
pip install -r requirements-dev.txt
black .
ruff check .
mypy custom_components tests
pytest
```

## Architecture

- `api.py`: PostgreSQL client, retry, timeout, and normalization
- `coordinator.py`: refresh orchestration through `DataUpdateCoordinator`
- `sensor.py`: Home Assistant entities
- `statistics.py`: historical import through recorder statistics APIs
- `diagnostics.py`: diagnostics payload generation
- `__init__.py`: entry setup, teardown, and service registration

## Local Review Checklist

- No generated files committed
- No unused imports or dead functions
- All new code typed
- Documentation updated
- Tests added or updated
