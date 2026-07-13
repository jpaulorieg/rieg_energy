"""Config flow for Rieg Energy."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .api import CannotConnect, RiegEnergyApiClient
from .const import (
    CONF_CONSUMER_UNIT,
    CONF_DATABASE,
    CONF_SSL,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SSL,
    DEFAULT_TIMEZONE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
)


class RiegEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rieg Energy."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow state."""
        self._validated_input: dict[str, Any] | None = None
        self._consumer_units: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await RiegEnergyApiClient.validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                self._validated_input = dict(user_input)
                try:
                    self._consumer_units = await RiegEnergyApiClient.async_list_consumer_units(
                        self.hass, self._validated_input
                    )
                except Exception:
                    errors["base"] = "unknown"
                else:
                    if not self._consumer_units:
                        errors["base"] = "no_consumer_units"
                    else:
                        return await self.async_step_consumer_unit()

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_DATABASE): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
                vol.Required(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL)),
                vol.Required(CONF_TIMEZONE, default=DEFAULT_TIMEZONE): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_consumer_unit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select the consumer unit for this integration entry."""
        errors: dict[str, str] = {}
        if self._validated_input is None or not self._consumer_units:
            return await self.async_step_user()

        if user_input is not None:
            selected_consumer_unit = user_input[CONF_CONSUMER_UNIT]
            entry_data = {
                **self._validated_input,
                CONF_CONSUMER_UNIT: selected_consumer_unit,
            }
            await self.async_set_unique_id(
                f"{entry_data[CONF_HOST]}:{entry_data[CONF_PORT]}/{entry_data[CONF_DATABASE]}/{selected_consumer_unit}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Rieg Energy ({selected_consumer_unit})",
                data=entry_data,
            )

        default_unit = self._consumer_units[0]
        schema = vol.Schema(
            {
                vol.Required(CONF_CONSUMER_UNIT, default=default_unit): vol.In(
                    self._consumer_units
                )
            }
        )
        return self.async_show_form(
            step_id="consumer_unit", data_schema=schema, errors=errors
        )
