"""Config flow tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant

from custom_components.rieg_energy.const import (
    CONF_DATABASE,
    CONF_SSL,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_TIMEZONE,
    DOMAIN,
)


async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful config flow."""
    with patch(
        "custom_components.rieg_energy.api.RiegEnergyApiClient.validate_input",
        new=AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert result["type"] == "form"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "localhost",
                CONF_PORT: 5432,
                CONF_DATABASE: "db",
                CONF_USERNAME: "user",
                CONF_PASSWORD: "secret",
                CONF_SSL: False,
                CONF_UPDATE_INTERVAL: 300,
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
            },
        )

    assert result["type"] == "create_entry"
    assert result["title"] == "Rieg Energy"


async def test_user_flow_connection_error(hass: HomeAssistant) -> None:
    """Test config flow connection error handling."""
    with patch(
        "custom_components.rieg_energy.api.RiegEnergyApiClient.validate_input",
        new=AsyncMock(side_effect=Exception("boom")),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "localhost",
                CONF_PORT: 5432,
                CONF_DATABASE: "db",
                CONF_USERNAME: "user",
                CONF_PASSWORD: "secret",
                CONF_SSL: False,
                CONF_UPDATE_INTERVAL: 300,
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
            },
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "unknown"}
