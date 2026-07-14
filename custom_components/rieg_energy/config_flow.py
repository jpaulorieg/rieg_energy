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
    DEFAULT_PORT,
    DEFAULT_SSL,
    DEFAULT_TIMEZONE,
    DOMAIN,
)


class RiegEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rieg Energy."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow state."""
        self._consumer_units: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_consumer_unit = str(user_input.get(CONF_CONSUMER_UNIT, "")).strip()
            connection_input = {
                key: value
                for key, value in user_input.items()
                if key != CONF_CONSUMER_UNIT
            }
            try:
                await RiegEnergyApiClient.validate_input(self.hass, connection_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                self._validated_input = dict(connection_input)
                try:
                    self._consumer_units = await RiegEnergyApiClient.async_list_consumer_units(
                        self.hass, connection_input
                    )
                except Exception:
                    errors["base"] = "unknown"
                else:
                    if not self._consumer_units:
                        errors["base"] = "no_consumer_units"
                    else:
                        if selected_consumer_unit not in self._consumer_units:
                            errors[CONF_CONSUMER_UNIT] = "invalid_consumer_unit"
                        else:
                            await self.async_set_unique_id(
                                f"{connection_input[CONF_HOST]}:{connection_input[CONF_PORT]}/{connection_input[CONF_DATABASE]}/{selected_consumer_unit}"
                            )
                            self._abort_if_unique_id_configured()
                            return self.async_create_entry(
                                title=f"Rieg Energy ({selected_consumer_unit})",
                                data={
                                    **connection_input,
                                    CONF_CONSUMER_UNIT: selected_consumer_unit,
                                },
                            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_DATABASE): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
                vol.Required(CONF_TIMEZONE, default=DEFAULT_TIMEZONE): str,
                vol.Required(CONF_CONSUMER_UNIT): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
