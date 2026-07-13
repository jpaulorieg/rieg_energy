"""Service tests."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from custom_components.rieg_energy import _async_register_services
from custom_components.rieg_energy.const import DOMAIN


async def test_register_services(hass: HomeAssistant) -> None:
    """Test service registration."""
    hass.data.setdefault(DOMAIN, {})
    await _async_register_services(hass)
    assert hass.services.has_service(DOMAIN, "sync_now")
