"""Coordinator for Rieg Energy."""

from __future__ import annotations

from collections import deque
from datetime import timedelta
from datetime import datetime
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AggregatedData, RiegEnergyApiClient
from .const import (
    COORDINATOR_RUNTIME_WINDOW,
    DEFAULT_UPDATE_INTERVAL,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


class RiegEnergyDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Handle fetching Rieg Energy data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: RiegEnergyApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="Rieg Energy",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.api = api
        self.last_sync: datetime | None = None
        self.runtime_durations: deque[float] = deque(maxlen=COORDINATOR_RUNTIME_WINDOW)

    async def _async_update_data(self) -> dict[str, Any]:
        started = dt_util.utcnow()
        try:
            snapshot = await self.api.async_get_snapshot()
        except Exception as err:
            raise UpdateFailed(str(err)) from err

        finished = dt_util.utcnow()
        self.last_sync = finished
        self.runtime_durations.append((finished - started).total_seconds())
        return self._as_dict(snapshot)

    def reset_runtime_metrics(self) -> None:
        """Clear runtime metrics."""
        self.runtime_durations.clear()

    def diagnostics_payload(self) -> dict[str, Any]:
        """Return diagnostics payload."""
        stats = self.api.get_runtime_stats()
        sensor_count = len(self.data["sensors"]) if self.data else 0
        return {
            "version": VERSION,
            "sensor_count": sensor_count,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "average_query_time": stats.average_query_time,
            "records_seen": stats.row_count,
            "query_count": stats.query_count,
            "last_error": stats.last_error,
        }

    def _as_dict(self, snapshot: AggregatedData) -> dict[str, Any]:
        sensors: dict[str, Any] = {
            "solar_power": snapshot.solar_power_w,
            "energy_today": snapshot.energy_today_kwh,
            "energy_week": snapshot.energy_week_kwh,
            "energy_month": snapshot.energy_month_kwh,
            "energy_year": snapshot.energy_year_kwh,
            "energy_total": snapshot.energy_total_kwh,
            **snapshot.weather,
            **snapshot.bill,
            **snapshot.bill_items,
            **snapshot.bill_readings,
        }
        return {
            "sensors": sensors,
            "metadata": {
                "last_sync": self.last_sync.isoformat() if self.last_sync else None,
                "history_rows": snapshot.imported_history_rows,
            },
        }
