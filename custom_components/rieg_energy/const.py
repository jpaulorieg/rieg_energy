"""Constants for the Rieg Energy integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "rieg_energy"
NAME: Final = "Rieg Energy"
VERSION: Final = "0.4.1"
ATTRIBUTION: Final = "Data provided by PostgreSQL"

CONF_DATABASE: Final = "database"
CONF_CONSUMER_UNIT: Final = "unidade_consumidora"
CONF_SSL: Final = "ssl"
CONF_TIMEZONE: Final = "timezone"
CONF_UPDATE_INTERVAL: Final = "update_interval"

DEFAULT_PORT: Final = 5432
DEFAULT_SSL: Final = False
DEFAULT_TIMEZONE: Final = "America/Sao_Paulo"
DEFAULT_UPDATE_INTERVAL: Final = 60
DEFAULT_TIMEOUT: Final = 10
DEFAULT_RETRY_ATTEMPTS: Final = 3
DEFAULT_RETRY_BASE: Final = 1.5
DEFAULT_BATCH_SIZE: Final = 128
DEFAULT_CURRENCY: Final = "BRL"

MIN_UPDATE_INTERVAL: Final = 60
MAX_UPDATE_INTERVAL: Final = 3600

COORDINATOR_RUNTIME_WINDOW: Final = 20
HISTORY_STORE_VERSION: Final = 1
HISTORY_STORE_KEY: Final = f"{DOMAIN}_history"
STATISTIC_ID_ENERGY_TOTAL: Final = f"{DOMAIN}:energy_total"
STATISTIC_SOURCE: Final = DOMAIN
STATISTICS_IMPORT_JOB_INTERVAL: Final = timedelta(minutes=30)

SERVICE_IMPORT_HISTORY: Final = "import_history"
SERVICE_REBUILD_STATISTICS: Final = "rebuild_statistics"
SERVICE_SYNC_NOW: Final = "sync_now"
SERVICE_CLEAR_CACHE: Final = "clear_cache"

SENSOR_KEY_SOLAR_POWER: Final = "solar_power"
SENSOR_KEY_ENERGY_TODAY: Final = "energy_today"
SENSOR_KEY_ENERGY_WEEK: Final = "energy_week"
SENSOR_KEY_ENERGY_MONTH: Final = "energy_month"
SENSOR_KEY_ENERGY_YEAR: Final = "energy_year"
SENSOR_KEY_ENERGY_TOTAL: Final = "energy_total"
