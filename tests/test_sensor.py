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
