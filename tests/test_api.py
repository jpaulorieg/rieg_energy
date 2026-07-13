"""API helper tests."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.rieg_energy.api import RiegEnergyApiClient


def test_find_first_value() -> None:
    """Test alias lookup."""
    client = RiegEnergyApiClient(
        hass=None,  # type: ignore[arg-type]
        host="localhost",
        port=5432,
        database="db",
        username="user",
        password="secret",
        ssl=False,
        timezone="America/Sao_Paulo",
        update_interval=300,
    )
    row = {"Valor_Total": 12.3}
    assert client._find_first_float(row, "valor_total") == 12.3


def test_sum_rows() -> None:
    """Test date-filtered aggregation."""
    client = RiegEnergyApiClient(
        hass=None,  # type: ignore[arg-type]
        host="localhost",
        port=5432,
        database="db",
        username="user",
        password="secret",
        ssl=False,
        timezone="America/Sao_Paulo",
        update_interval=300,
    )
    rows = [
        {"observed_on": date(2026, 7, 1), "energy_kwh": 10.0},
        {"observed_on": date(2026, 7, 2), "energy_kwh": 12.5},
    ]
    assert client._sum_rows(rows, None) == 22.5
    assert client._sum_rows(rows, date(2026, 7, 2)) == 12.5


async def test_async_execute_uses_psycopg_async_connection() -> None:
    """Test that query execution uses psycopg3 async connection APIs."""
    client = RiegEnergyApiClient(
        hass=None,  # type: ignore[arg-type]
        host="localhost",
        port=5432,
        database="db",
        username="user",
        password="secret",
        ssl=False,
        timezone="America/Sao_Paulo",
        update_interval=300,
    )

    connection = MagicMock()
    cursor = AsyncMock()
    cursor.__aenter__.return_value = cursor
    cursor.__aexit__.return_value = None
    cursor.fetchall.return_value = [{"value": 1}]
    connection.cursor.return_value = cursor

    with patch(
        "custom_components.rieg_energy.api.AsyncConnection.connect",
        new=AsyncMock(return_value=connection),
    ) as connect_mock:
        rows = await client.async_execute("SELECT 1", cache_key=None)

    assert rows == [{"value": 1}]
    connect_mock.assert_awaited_once()
