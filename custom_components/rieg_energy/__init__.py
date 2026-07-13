"""The Rieg Energy integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .api import RiegEnergyApiClient
from .const import (
    DOMAIN,
    SERVICE_CLEAR_CACHE,
    SERVICE_IMPORT_HISTORY,
    SERVICE_REBUILD_STATISTICS,
    SERVICE_SYNC_NOW,
)
from .coordinator import RiegEnergyDataUpdateCoordinator
from .services import ENTRY_SERVICE_SCHEMA, IMPORT_HISTORY_SCHEMA
from .statistics import RiegEnergyStatisticsImporter

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: Mapping[str, Any]) -> bool:
    """Set up the Rieg Energy integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rieg Energy from a config entry."""
    api = RiegEnergyApiClient.from_entry_data(hass, entry)
    coordinator = RiegEnergyDataUpdateCoordinator(hass, entry, api)
    importer = RiegEnergyStatisticsImporter(hass, entry, api, coordinator)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "statistics": importer,
    }

    await _async_register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        api: RiegEnergyApiClient = data["api"]
        await api.async_close()

    if not hass.data[DOMAIN]:
        for service in (
            SERVICE_IMPORT_HISTORY,
            SERVICE_REBUILD_STATISTICS,
            SERVICE_SYNC_NOW,
            SERVICE_CLEAR_CACHE,
        ):
            hass.services.async_remove(DOMAIN, service)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register integration services once."""
    if hass.services.has_service(DOMAIN, SERVICE_IMPORT_HISTORY):
        return

    async def async_require_entry(call: ServiceCall) -> ConfigEntry:
        entry_id = call.data.get("entry_id")
        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry and entry.domain == DOMAIN:
                return entry
            raise HomeAssistantError(f"Config entry '{entry_id}' not found")

        entries = hass.config_entries.async_entries(DOMAIN)
        if len(entries) != 1:
            raise HomeAssistantError(
                "Service requires entry_id when more than one Rieg Energy entry exists"
            )
        return entries[0]

    async def async_handle_import_history(call: ServiceCall) -> None:
        entry = await async_require_entry(call)
        importer: RiegEnergyStatisticsImporter = hass.data[DOMAIN][entry.entry_id][
            "statistics"
        ]
        await importer.async_import_history(force_full=bool(call.data.get("force_full")))

    async def async_handle_rebuild_statistics(call: ServiceCall) -> None:
        entry = await async_require_entry(call)
        importer: RiegEnergyStatisticsImporter = hass.data[DOMAIN][entry.entry_id][
            "statistics"
        ]
        await importer.async_rebuild_statistics()

    async def async_handle_sync_now(call: ServiceCall) -> None:
        entry = await async_require_entry(call)
        coordinator: RiegEnergyDataUpdateCoordinator = hass.data[DOMAIN][
            entry.entry_id
        ]["coordinator"]
        await coordinator.async_request_refresh()

    async def async_handle_clear_cache(call: ServiceCall) -> None:
        entry = await async_require_entry(call)
        api: RiegEnergyApiClient = hass.data[DOMAIN][entry.entry_id]["api"]
        coordinator: RiegEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
            "coordinator"
        ]
        api.clear_cache()
        coordinator.reset_runtime_metrics()
        _LOGGER.info("Cache cleared for entry %s", entry.entry_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_IMPORT_HISTORY,
        async_handle_import_history,
        schema=IMPORT_HISTORY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REBUILD_STATISTICS,
        async_handle_rebuild_statistics,
        schema=ENTRY_SERVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SYNC_NOW,
        async_handle_sync_now,
        schema=ENTRY_SERVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_CACHE,
        async_handle_clear_cache,
        schema=ENTRY_SERVICE_SCHEMA,
    )
