"""Config flow tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant

from custom_components.rieg_energy.const import (
    CONF_CONSUMER_UNIT,
    CONF_DATABASE,
    CONF_SSL,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_TIMEZONE,
    DOMAIN,
)


async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful config flow."""
    with (
        patch(
            "custom_components.rieg_energy.api.RiegEnergyApiClient.validate_input",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.rieg_energy.api.RiegEnergyApiClient.async_list_consumer_units",
            new=AsyncMock(return_value=["UC-001", "UC-002"]),
        ),
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

        assert result["type"] == "form"
        assert result["step_id"] == "consumer_unit"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_CONSUMER_UNIT: "UC-002"},
        )

    assert result["type"] == "create_entry"
    assert result["title"] == "Rieg Energy (UC-002)"
    assert result["data"][CONF_CONSUMER_UNIT] == "UC-002"


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
