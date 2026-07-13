"""API helper tests."""

from __future__ import annotations

from datetime import date
from datetime import time
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


def test_normalize_weather_maps_meteoblue_ddl_columns() -> None:
    """Test weather normalization using meteoblue.solar_weather column names."""
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

    row = {
        "sunshine_time": time(5, 30),
        "totalcloudcover_mean": 42.4,
        "dni_total": 610.2,
        "ghi_total": 520.8,
        "dif_total": 98.7,
        "directshortwaveradiation_total": 501.0,
    }

    weather = client._normalize_weather(row)

    assert weather["sunshine_time"] == 330.0
    assert weather["cloud_cover"] == 42.4
    assert weather["dni"] == 610.2
    assert weather["ghi"] == 520.8
    assert weather["dif"] == 98.7
    assert weather["solar_radiation"] == 501.0


def test_normalize_bill_maps_fatura_ddl_columns() -> None:
    """Test bill normalization using fatura column names."""
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

    bill = client._normalize_bill(
        {
            "total_pagar": 285.44,
            "referencia": "2026-07",
            "vencimento": date(2026, 8, 10),
        }
    )

    assert bill["last_bill"] == 285.44
    assert bill["reference_month"] == "2026-07"
    assert bill["bill_due_date"] == date(2026, 8, 10)


def test_normalize_bill_items_maps_fatura_item_ddl_columns() -> None:
    """Test bill item normalization from fatura_item rows."""
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

    items = client._normalize_bill_items(
        [
            {"descricao_item": "Energia TE", "quantidade": 120.0, "valor": 90.0},
            {"descricao_item": "Energia TUSD", "quantidade": 100.0, "valor": 80.0},
            {"descricao_item": "Energia Injetada", "quantidade": 50.0, "valor": -30.0},
            {"descricao_item": "Energia Consumida", "quantidade": 150.0, "valor": 140.0},
        ],
        {"modalidade_tarifaria": "Verde"},
    )

    assert items["average_price"] == 0.667
    assert items["energy_te"] == 120.0
    assert items["energy_tusd"] == 100.0
    assert items["tariff_flag"] == "Verde"
    assert items["injected_value"] == 30.0
    assert items["consumed_value"] == 140.0


def test_normalize_bill_readings_maps_fatura_leitura_ddl_columns() -> None:
    """Test bill reading normalization from fatura_leitura rows."""
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

    readings = client._normalize_bill_readings(
        [
            {
                "grandeza": "Energia ativa consumida",
                "total_apurado": 340.0,
                "leitura_anterior": 1000.0,
                "leitura_atual": 1250.0,
            },
            {
                "grandeza": "Energia ativa injetada",
                "total_apurado": -210.0,
                "leitura_anterior": 400.0,
                "leitura_atual": 610.0,
            },
        ]
    )

    assert readings["energy_consumed"] == 340.0
    assert readings["energy_injected"] == 210.0
    assert readings["previous_reading"] == 1000.0
    assert readings["current_reading"] == 1250.0
    assert readings["reading_difference"] == 250.0


async def test_async_get_snapshot_filters_latest_bill_by_consumer_unit() -> None:
    """Test snapshot query filters latest bill by selected unidade_consumidora."""
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
        consumer_unit="UC-001",
    )

    client.async_execute = AsyncMock(
        side_effect=[
            [{"solar_power_w": 1200.0}],
            [{"observed_on": date(2026, 7, 1), "energy_kwh": 12.0}],
            [{"ghi_total": 510.0}],
            [{"id": 10, "total_pagar": 200.0, "referencia": "2026-07", "vencimento": date(2026, 8, 10)}],
            [{"id_fatura": 10, "descricao_item": "Energia TE", "quantidade": 100.0, "valor": 80.0}],
            [{"id_fatura": 10, "grandeza": "Energia ativa consumida", "total_apurado": 300.0, "leitura_anterior": 1000.0, "leitura_atual": 1300.0}],
        ]
    )

    await client.async_get_snapshot()

    hourly_query = client.async_execute.await_args_list[0].args[0]
    assert "hour_producer < EXTRACT(HOUR" in hourly_query
    assert "hour_producer = EXTRACT(HOUR" in hourly_query
    assert "AND minute_producer <= EXTRACT(MINUTE" in hourly_query

    bill_query = client.async_execute.await_args_list[3].args[0]
    assert "unidade_consumidora" in bill_query

    bill_item_query = client.async_execute.await_args_list[4].args[0]
    assert "JOIN fatura_item" in bill_item_query
    assert "id_fatura" in bill_item_query

    bill_reading_query = client.async_execute.await_args_list[5].args[0]
    assert "JOIN fatura_leitura" in bill_reading_query
    assert "id_fatura" in bill_reading_query
