"""Sensor tests."""

from __future__ import annotations

from datetime import date

from custom_components.rieg_energy.sensor import RiegEnergySensor, SENSORS


def test_sensor_native_value(entry, snapshot_data) -> None:
    """Test sensor value resolution."""
    coordinator = type("Coordinator", (), {"data": snapshot_data})()
    sensor = RiegEnergySensor(coordinator, entry, SENSORS[0])
    assert sensor.native_value == 1234.0


def test_sensor_date_native_value(entry, snapshot_data) -> None:
    """Test date conversion for date-class sensors."""
    snapshot_data["sensors"]["bill_due_date"] = "2026-07-31"
    coordinator = type("Coordinator", (), {"data": snapshot_data})()
    date_sensor = next(
        description for description in SENSORS if description.key == "bill_due_date"
    )
    sensor = RiegEnergySensor(coordinator, entry, date_sensor)
    assert sensor.native_value == date(2026, 7, 31)


def test_sensor_device_info_uses_generation_device(entry, snapshot_data) -> None:
    """Test generation sensors are attached to the generation device."""
    coordinator = type("Coordinator", (), {"data": snapshot_data})()
    generation_sensor = next(
        description for description in SENSORS if description.key == "solar_power"
    )
    sensor = RiegEnergySensor(coordinator, entry, generation_sensor)

    assert sensor._attr_device_info["identifiers"] == {("rieg_energy", "test-entry_producer")}
    assert sensor._attr_device_info["name"] == "Rieg Energy - Geração"


def test_sensor_device_info_uses_bill_device(entry, snapshot_data) -> None:
    """Test bill sensors are attached to the bill device."""
    coordinator = type("Coordinator", (), {"data": snapshot_data})()
    bill_sensor = next(
        description for description in SENSORS if description.key == "last_bill"
    )
    sensor = RiegEnergySensor(coordinator, entry, bill_sensor)

    assert sensor._attr_device_info["identifiers"] == {("rieg_energy", "test-entry_bill")}
    assert sensor._attr_device_info["name"] == "Rieg Energy - Fatura"


def test_sensor_device_info_uses_predict_device(entry, snapshot_data) -> None:
    """Test prediction sensors are attached to the predict device."""
    coordinator = type("Coordinator", (), {"data": snapshot_data})()
    predict_sensor = next(
        description for description in SENSORS if description.key == "producer_predict"
    )
    sensor = RiegEnergySensor(coordinator, entry, predict_sensor)

    assert sensor._attr_device_info["identifiers"] == {
        ("rieg_energy", "test-entry_predict_device")
    }
    assert sensor._attr_device_info["name"] == "predict_device"
    assert sensor.native_value == 15.75


def test_meteoblue_sensors_use_predict_device(entry, snapshot_data) -> None:
    """Test Meteoblue-derived sensors are attached to the predict device."""
    coordinator = type("Coordinator", (), {"data": snapshot_data})()
    weather_sensor = next(
        description for description in SENSORS if description.key == "solar_radiation"
    )
    sensor = RiegEnergySensor(coordinator, entry, weather_sensor)

    assert sensor._attr_device_info["identifiers"] == {
        ("rieg_energy", "test-entry_predict_device")
    }
    assert sensor._attr_device_info["name"] == "predict_device"
