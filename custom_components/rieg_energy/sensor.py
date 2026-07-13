"""Sensor platform for Rieg Energy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DEFAULT_CURRENCY, DOMAIN
from .coordinator import RiegEnergyDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class RiegEnergySensorDescription(SensorEntityDescription):
    """Describe a Rieg Energy sensor."""

    value_key: str


SENSORS: tuple[RiegEnergySensorDescription, ...] = (
    RiegEnergySensorDescription(
        key="solar_power",
        translation_key="solar_power",
        name="Solar Power",
        value_key="solar_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="energy_today",
        translation_key="energy_today",
        name="Energy Today",
        value_key="energy_today",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    RiegEnergySensorDescription(
        key="energy_week",
        translation_key="energy_week",
        name="Energy Week",
        value_key="energy_week",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    RiegEnergySensorDescription(
        key="energy_month",
        translation_key="energy_month",
        name="Energy Month",
        value_key="energy_month",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    RiegEnergySensorDescription(
        key="energy_year",
        translation_key="energy_year",
        name="Energy Year",
        value_key="energy_year",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    RiegEnergySensorDescription(
        key="energy_total",
        translation_key="energy_total",
        name="Energy Total",
        value_key="energy_total",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    RiegEnergySensorDescription(
        key="forecast_generation",
        translation_key="forecast_generation",
        name="Forecast Generation",
        value_key="forecast_generation",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="solar_radiation",
        translation_key="solar_radiation",
        name="Solar Radiation",
        value_key="solar_radiation",
        device_class=SensorDeviceClass.IRRADIANCE,
        native_unit_of_measurement="W/m2",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="cloud_cover",
        translation_key="cloud_cover",
        name="Cloud Cover",
        value_key="cloud_cover",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="sunshine_time",
        translation_key="sunshine_time",
        name="Sunshine Time",
        value_key="sunshine_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="dni",
        translation_key="dni",
        name="DNI",
        value_key="dni",
        device_class=SensorDeviceClass.IRRADIANCE,
        native_unit_of_measurement="W/m2",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="ghi",
        translation_key="ghi",
        name="GHI",
        value_key="ghi",
        device_class=SensorDeviceClass.IRRADIANCE,
        native_unit_of_measurement="W/m2",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="dif",
        translation_key="dif",
        name="DIF",
        value_key="dif",
        device_class=SensorDeviceClass.IRRADIANCE,
        native_unit_of_measurement="W/m2",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="last_bill",
        translation_key="last_bill",
        name="Last Bill",
        value_key="last_bill",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=DEFAULT_CURRENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="reference_month",
        translation_key="reference_month",
        name="Reference Month",
        value_key="reference_month",
    ),
    RiegEnergySensorDescription(
        key="bill_due_date",
        translation_key="bill_due_date",
        name="Bill Due Date",
        value_key="bill_due_date",
        device_class=SensorDeviceClass.DATE,
    ),
    RiegEnergySensorDescription(
        key="average_price",
        translation_key="average_price",
        name="Average Price",
        value_key="average_price",
        native_unit_of_measurement="BRL/kWh",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="energy_te",
        translation_key="energy_te",
        name="Energy TE",
        value_key="energy_te",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="energy_tusd",
        translation_key="energy_tusd",
        name="Energy TUSD",
        value_key="energy_tusd",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="tariff_flag",
        translation_key="tariff_flag",
        name="Tariff Flag",
        value_key="tariff_flag",
    ),
    RiegEnergySensorDescription(
        key="injected_value",
        translation_key="injected_value",
        name="Injected Value",
        value_key="injected_value",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=DEFAULT_CURRENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="consumed_value",
        translation_key="consumed_value",
        name="Consumed Value",
        value_key="consumed_value",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=DEFAULT_CURRENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    RiegEnergySensorDescription(
        key="energy_consumed",
        translation_key="energy_consumed",
        name="Energy Consumed",
        value_key="energy_consumed",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    RiegEnergySensorDescription(
        key="energy_injected",
        translation_key="energy_injected",
        name="Energy Injected",
        value_key="energy_injected",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    RiegEnergySensorDescription(
        key="previous_reading",
        translation_key="previous_reading",
        name="Previous Reading",
        value_key="previous_reading",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    RiegEnergySensorDescription(
        key="current_reading",
        translation_key="current_reading",
        name="Current Reading",
        value_key="current_reading",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    RiegEnergySensorDescription(
        key="reading_difference",
        translation_key="reading_difference",
        name="Reading Difference",
        value_key="reading_difference",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Rieg Energy sensors."""
    coordinator: RiegEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities(
        RiegEnergySensor(coordinator, entry, description) for description in SENSORS
    )


class RiegEnergySensor(CoordinatorEntity[RiegEnergyDataUpdateCoordinator], SensorEntity):
    """Representation of a Rieg Energy sensor."""

    entity_description: RiegEnergySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RiegEnergyDataUpdateCoordinator,
        entry: ConfigEntry,
        description: RiegEnergySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_attribution = ATTRIBUTION
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "manufacturer": "Rieg",
            "model": "PostgreSQL Energy Integration",
            "name": "Rieg Energy",
        }

    @property
    def native_value(self) -> Any:
        value = self.coordinator.data["sensors"].get(self.entity_description.value_key)
        if self.entity_description.device_class is SensorDeviceClass.DATE:
            if isinstance(value, str):
                return date.fromisoformat(value)
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, date):
                return value
        return value
