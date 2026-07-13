"""Coordinator tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant

from custom_components.rieg_energy.coordinator import RiegEnergyDataUpdateCoordinator


async def test_coordinator_refresh(
    hass: HomeAssistant, entry, snapshot_data: dict[str, object]
) -> None:
    """Test coordinator refresh."""
    api = AsyncMock()
    api.async_get_snapshot.return_value = type(
        "Snapshot",
        (),
        {
            "solar_power_w": 1234.0,
            "energy_today_kwh": 12.3,
            "energy_week_kwh": 44.1,
            "energy_month_kwh": 180.4,
            "energy_year_kwh": 1200.0,
            "energy_total_kwh": 5400.2,
            "weather": {
                "forecast_generation": 14.1,
                "solar_radiation": 500.0,
                "cloud_cover": 20.0,
                "sunshine_time": 300.0,
                "dni": 700.0,
                "ghi": 650.0,
                "dif": 100.0,
            },
            "bill": {"last_bill": 220.55, "reference_month": "2026-06", "bill_due_date": None},
            "bill_items": {
                "average_price": 0.89,
                "energy_te": 110.0,
                "energy_tusd": 95.0,
                "tariff_flag": "green",
                "injected_value": 45.2,
                "consumed_value": 175.35,
            },
            "bill_readings": {
                "energy_consumed": 340.0,
                "energy_injected": 210.0,
                "previous_reading": 1000.0,
                "current_reading": 1250.0,
                "reading_difference": 250.0,
            },
            "imported_history_rows": 10,
        },
    )()
    api.get_runtime_stats.return_value = type(
        "RuntimeStats",
        (),
        {"average_query_time": 0.4, "row_count": 12, "query_count": 4, "last_error": None},
    )()

    coordinator = RiegEnergyDataUpdateCoordinator(hass, entry, api)
    await coordinator.async_refresh()

    assert coordinator.last_update_success is True
    assert coordinator.data["sensors"]["energy_total"] == 5400.2


async def test_coordinator_diagnostics(hass: HomeAssistant, entry) -> None:
    """Test diagnostics payload generation."""
    api = AsyncMock()
    api.get_runtime_stats.return_value = type(
        "RuntimeStats",
        (),
        {"average_query_time": 0.7, "row_count": 5, "query_count": 2, "last_error": None},
    )()
    coordinator = RiegEnergyDataUpdateCoordinator(hass, entry, api)
    coordinator.data = {"sensors": {"solar_power": 1.0}, "metadata": {}}

    diagnostics = coordinator.diagnostics_payload()

    assert diagnostics["sensor_count"] == 1
    assert diagnostics["query_count"] == 2
