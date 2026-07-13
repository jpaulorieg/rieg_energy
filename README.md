# Rieg Energy

[![CI](https://github.com/Rieg/rieg_energy/actions/workflows/ci.yml/badge.svg)](https://github.com/Rieg/rieg_energy/actions/workflows/ci.yml)
[![Hassfest](https://github.com/Rieg/rieg_energy/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Rieg/rieg_energy/actions/workflows/hassfest.yml)
[![Release](https://github.com/Rieg/rieg_energy/actions/workflows/release.yml/badge.svg)](https://github.com/Rieg/rieg_energy/actions/workflows/release.yml)
[![Coverage Target](https://img.shields.io/badge/coverage-target%2095%25-brightgreen)](./pyproject.toml)
[![Version](https://img.shields.io/badge/version-0.4.1-blue)](./custom_components/rieg_energy/manifest.json)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.1.4-blue)](./hacs.json)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](./pyproject.toml)

Home Assistant custom integration that reads energy, billing, and solar forecast data directly from PostgreSQL and exposes them as native Home Assistant entities. Historical solar production is imported through the official recorder statistics APIs only.

## Highlights

- UI setup through Config Flow
- Async PostgreSQL access with `psycopg3`
- `DataUpdateCoordinator`-based refresh orchestration
- Historical statistics import with `async_add_external_statistics`
- Diagnostics support
- HACS-compatible repository structure
- GitHub CI, release workflow, and Hassfest workflow

## Compatibility

- Home Assistant: `2026.x` or newer target in this repository setup
- Python: `3.13+` for the project metadata
- PostgreSQL: supported

## Installation

### Manual

1. Copy `custom_components/rieg_energy` into your Home Assistant configuration directory under `custom_components/`.
2. Restart Home Assistant.
3. Add the `Rieg Energy` integration from the UI.

### HACS

1. Add this repository as a custom integration repository in HACS.
2. Install `Rieg Energy`.
3. Restart Home Assistant.
4. Configure the integration from the UI.

Detailed setup:

- [Installation](./docs/installation.md)
- [PostgreSQL](./docs/postgres.md)
- [Statistics](./docs/statistics.md)
- [Dashboard](./docs/dashboard.md)
- [Development](./docs/development.md)
- [FAQ](./docs/faq.md)

## Configuration Inputs

- Hostname
- Port
- Database
- Username
- Password
- SSL
- Update interval
- Timezone

## Entities

### Solar Production

- `sensor.solar_power`
- `sensor.energy_today`
- `sensor.energy_week`
- `sensor.energy_month`
- `sensor.energy_year`
- `sensor.energy_total`

### Solar Forecast

- `sensor.forecast_generation`
- `sensor.solar_radiation`
- `sensor.cloud_cover`
- `sensor.sunshine_time`
- `sensor.dni`
- `sensor.ghi`
- `sensor.dif`

### Billing

- `sensor.last_bill`
- `sensor.reference_month`
- `sensor.bill_due_date`
- `sensor.average_price`
- `sensor.energy_te`
- `sensor.energy_tusd`
- `sensor.tariff_flag`
- `sensor.injected_value`
- `sensor.consumed_value`

### Meter Readings

- `sensor.energy_consumed`
- `sensor.energy_injected`
- `sensor.previous_reading`
- `sensor.current_reading`
- `sensor.reading_difference`

## Services

- `rieg_energy.import_history`
- `rieg_energy.rebuild_statistics`
- `rieg_energy.sync_now`
- `rieg_energy.clear_cache`

## Screenshots

Placeholder images:

![Energy Dashboard Placeholder](https://via.placeholder.com/1280x720?text=Energy+Dashboard+Placeholder)
![Entities Placeholder](https://via.placeholder.com/1280x720?text=Entities+Placeholder)

## Development

```bash
pip install -r requirements-dev.txt
black .
ruff check .
mypy custom_components tests
pytest
```

Coverage target:

- Minimum `95%`

## Notes

- The integration is read-only against PostgreSQL.
- The connector uses `psycopg3` with binary wheels to avoid native compilation steps in Home Assistant environments.
- It does not use the Growatt API.
- It does not write directly to the Home Assistant database.
- Some weather and billing mappings use column aliases because the specification does not define every physical column name for those tables.
- Weather mapping for `meteoblue.solar_weather` supports `sunshine_time` (`time` to minutes), `dni_total`, `ghi_total`, `dif_total`, `totalcloudcover_mean`, and `directshortwaveradiation_total` (plus backward-compatible aliases).
