"""Fixtures for Rieg Energy tests."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

from custom_components.rieg_energy.const import (
    CONF_DATABASE,
    CONF_SSL,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_TIMEZONE,
    DOMAIN,
)


@pytest.fixture
def entry() -> ConfigEntry:
    """Return a mock config entry."""
    return cast(
        ConfigEntry,
        MagicMock(
            entry_id="test-entry",
            domain=DOMAIN,
            version=1,
            data={
                CONF_HOST: "localhost",
                CONF_PORT: 5432,
                CONF_DATABASE: "solar",
                CONF_USERNAME: "solar",
                CONF_PASSWORD: "secret",
                CONF_SSL: False,
                CONF_UPDATE_INTERVAL: 300,
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
            },
        ),
    )


@pytest.fixture
def snapshot_data() -> dict[str, Any]:
    """Return a coordinator snapshot."""
    return {
        "sensors": {
            "solar_power": 1234.0,
            "energy_today": 12.3,
            "energy_week": 44.1,
            "energy_month": 180.4,
            "energy_year": 1200.0,
            "energy_total": 5400.2,
            "forecast_generation": 14.1,
            "solar_radiation": 500.0,
            "cloud_cover": 20.0,
            "sunshine_time": 300.0,
            "dni": 700.0,
            "ghi": 650.0,
            "dif": 100.0,
            "last_bill": 220.55,
            "reference_month": "2026-06",
            "bill_due_date": None,
            "average_price": 0.89,
            "energy_te": 110.0,
            "energy_tusd": 95.0,
            "tariff_flag": "green",
            "injected_value": 45.2,
            "consumed_value": 175.35,
            "energy_consumed": 340.0,
            "energy_injected": 210.0,
            "previous_reading": 1000.0,
            "current_reading": 1250.0,
            "reading_difference": 250.0,
        },
        "metadata": {"last_sync": "2026-07-12T00:00:00+00:00", "history_rows": 10},
    }
