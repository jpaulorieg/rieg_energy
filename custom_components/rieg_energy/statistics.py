"""Historical statistics support for Rieg Energy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import storage
from homeassistant.util import dt as dt_util

from .api import RiegEnergyApiClient
from .const import (
    DEFAULT_BATCH_SIZE,
    HISTORY_STORE_KEY,
    HISTORY_STORE_VERSION,
    STATISTIC_ID_ENERGY_TOTAL,
    STATISTIC_SOURCE,
)
from .coordinator import RiegEnergyDataUpdateCoordinator

try:
    from homeassistant.components.recorder.statistics import (
        StatisticData,
        StatisticMetaData,
        async_add_external_statistics,
        async_clear_statistics,
    )
except ImportError:  # pragma: no cover - compatibility shim for older cores
    from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
    from homeassistant.components.recorder.statistics import async_add_external_statistics

    async def async_clear_statistics(  # type: ignore[override]
        hass: HomeAssistant, statistic_ids: list[str]
    ) -> None:
        raise NotImplementedError("async_clear_statistics is unavailable in this Home Assistant version")

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ImportProgress:
    """Persistence model for import progress."""

    last_imported_date: str | None = None
    imported_rows: int = 0
    total_sum_kwh: float = 0.0
    last_error: str | None = None
    updated_at: str | None = None


class RiegEnergyStatisticsImporter:
    """Import external statistics into Home Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: RiegEnergyApiClient,
        coordinator: RiegEnergyDataUpdateCoordinator,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.api = api
        self.coordinator = coordinator
        self._store = storage.Store[dict[str, Any]](
            hass,
            HISTORY_STORE_VERSION,
            f"{HISTORY_STORE_KEY}_{entry.entry_id}.json",
        )

    async def async_import_history(self, *, force_full: bool = False) -> None:
        """Import daily energy history from PostgreSQL."""
        progress = await self._async_load_progress()
        start_date = None if force_full else self._next_start_date(progress.last_imported_date)
        sum_kwh = 0.0 if force_full else progress.total_sum_kwh

        while True:
            try:
                rows = await self.api.async_get_monthly_history(
                    start_date=start_date,
                    batch_size=DEFAULT_BATCH_SIZE,
                )
                if not rows:
                    break

                statistic_rows: list[StatisticData] = []
                for row in rows:
                    energy_kwh = row["energy_kwh"]
                    observed_on: date = row["observed_on"]
                    sum_kwh += energy_kwh
                    statistic_rows.append(
                        StatisticData(
                            start=self._as_local_midnight(observed_on),
                            state=energy_kwh,
                            sum=sum_kwh,
                        )
                    )

                await async_add_external_statistics(
                    self.hass,
                    StatisticMetaData(
                        has_mean=False,
                        has_sum=True,
                        name="Rieg Energy Total",
                        source=STATISTIC_SOURCE,
                        statistic_id=STATISTIC_ID_ENERGY_TOTAL,
                        unit_of_measurement="kWh",
                    ),
                    statistic_rows,
                )

                progress.imported_rows += len(rows)
                progress.last_imported_date = rows[-1]["observed_on"].isoformat()
                progress.total_sum_kwh = sum_kwh
                progress.last_error = None
                progress.updated_at = dt_util.utcnow().isoformat()
                await self._store.async_save(progress.__dict__)

                _LOGGER.info(
                    "Imported %s statistics rows up to %s",
                    len(rows),
                    progress.last_imported_date,
                )
                start_date = rows[-1]["observed_on"] + timedelta(days=1)
            except Exception as err:
                progress.last_error = str(err)
                progress.updated_at = dt_util.utcnow().isoformat()
                await self._store.async_save(progress.__dict__)
                _LOGGER.exception("Statistics import failed")
                raise

    async def async_rebuild_statistics(self) -> None:
        """Clear and rebuild imported statistics."""
        await async_clear_statistics(self.hass, [STATISTIC_ID_ENERGY_TOTAL])
        await self._store.async_save(ImportProgress().__dict__)
        await self.async_import_history(force_full=True)

    async def _async_load_progress(self) -> ImportProgress:
        data = await self._store.async_load()
        if data is None:
            return ImportProgress()
        return ImportProgress(**data)

    def _next_start_date(self, last_imported_date: str | None) -> date | None:
        if not last_imported_date:
            return None
        return date.fromisoformat(last_imported_date) + timedelta(days=1)

    def _as_local_midnight(self, value: date) -> datetime:
        tzinfo = dt_util.get_time_zone(self.api.timezone)
        return datetime.combine(value, time.min, tzinfo=tzinfo).astimezone(UTC)
