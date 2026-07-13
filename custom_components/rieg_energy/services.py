"""Service schemas for Rieg Energy."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

IMPORT_HISTORY_SCHEMA = vol.Schema(
    {
        vol.Optional("entry_id"): cv.string,
        vol.Optional("force_full", default=False): cv.boolean,
    }
)

ENTRY_SERVICE_SCHEMA = vol.Schema({vol.Optional("entry_id"): cv.string})
