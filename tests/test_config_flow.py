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
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
                CONF_CONSUMER_UNIT: "UC-002",
            },
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
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
                CONF_CONSUMER_UNIT: "UC-001",
            },
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "unknown"}


async def test_user_flow_direct_consumer_unit_on_first_step(hass: HomeAssistant) -> None:
    """Test successful entry creation when unidade_consumidora is informed."""
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
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "localhost",
                CONF_PORT: 5432,
                CONF_DATABASE: "db",
                CONF_USERNAME: "user",
                CONF_PASSWORD: "secret",
                CONF_SSL: False,
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
                CONF_CONSUMER_UNIT: "UC-001",
            },
        )

    assert result["type"] == "create_entry"
    assert result["data"][CONF_CONSUMER_UNIT] == "UC-001"


async def test_user_flow_requires_consumer_unit(hass: HomeAssistant) -> None:
    """Test that unidade_consumidora is required in first step."""
    with patch(
        "custom_components.rieg_energy.api.RiegEnergyApiClient.validate_input",
        new=AsyncMock(),
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
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
            },
        )

    assert result["type"] == "form"


async def test_user_flow_invalid_consumer_unit_on_first_step(hass: HomeAssistant) -> None:
    """Test validation error for unknown unidade_consumidora on first step."""
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
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "localhost",
                CONF_PORT: 5432,
                CONF_DATABASE: "db",
                CONF_USERNAME: "user",
                CONF_PASSWORD: "secret",
                CONF_SSL: False,
                CONF_TIMEZONE: DEFAULT_TIMEZONE,
                CONF_CONSUMER_UNIT: "UC-999",
            },
        )

    assert result["type"] == "form"
    assert result["errors"][CONF_CONSUMER_UNIT] == "invalid_consumer_unit"
