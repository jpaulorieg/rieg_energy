"""Statistics tests."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant

from custom_components.rieg_energy.statistics import ImportProgress
from custom_components.rieg_energy.statistics import RiegEnergyStatisticsImporter


async def test_statistics_import(hass: HomeAssistant, entry) -> None:
    """Test statistics import batches."""
    api = AsyncMock()
    api.timezone = "America/Sao_Paulo"
    api.async_get_monthly_history.side_effect = [
        [
            {"observed_on": date(2026, 7, 1), "energy_kwh": 10.0},
            {"observed_on": date(2026, 7, 2), "energy_kwh": 12.0},
        ],
        [],
    ]
    coordinator = AsyncMock()

    with patch(
        "custom_components.rieg_energy.statistics.async_add_external_statistics",
        new=AsyncMock(),
    ) as add_stats:
        importer = RiegEnergyStatisticsImporter(hass, entry, api, coordinator)
        await importer.async_import_history(force_full=True)

    assert add_stats.await_count == 1


async def test_statistics_next_start_date(hass: HomeAssistant, entry) -> None:
    """Test checkpoint start date calculation."""
    importer = RiegEnergyStatisticsImporter(hass, entry, AsyncMock(), AsyncMock())
    assert importer._next_start_date("2026-07-01") == date(2026, 7, 2)
    assert importer._next_start_date(None) is None


async def test_statistics_load_progress_default(hass: HomeAssistant, entry) -> None:
    """Test empty progress store."""
    importer = RiegEnergyStatisticsImporter(hass, entry, AsyncMock(), AsyncMock())
    progress = await importer._async_load_progress()
    assert progress == ImportProgress()
