"""Async PostgreSQL client for Rieg Energy."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import logging
from statistics import fmean
from time import perf_counter
from typing import Any, Final

import psycopg
from psycopg import AsyncConnection
from psycopg.rows import dict_row
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CONSUMER_UNIT,
    CONF_DATABASE,
    CONF_SSL,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_BATCH_SIZE,
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_BASE,
    DEFAULT_SSL,
    DEFAULT_TIMEOUT,
    DEFAULT_TIMEZONE,
)

_LOGGER = logging.getLogger(__name__)

QUERY_CACHE_TTL: Final = timedelta(minutes=5)


class CannotConnect(ConfigEntryError):
    """Error to indicate we cannot connect."""


@dataclass(slots=True)
class QueryMetric:
    """Runtime metric for a query execution."""

    elapsed: float
    rows: int


@dataclass(slots=True)
class RuntimeStats:
    """Runtime statistics for diagnostics."""

    query_count: int = 0
    row_count: int = 0
    last_error: str | None = None
    average_query_time: float = 0.0


@dataclass(slots=True)
class AggregatedData:
    """Normalized integration payload."""

    solar_power_w: float | None
    energy_today_kwh: float | None
    energy_week_kwh: float | None
    energy_month_kwh: float | None
    energy_year_kwh: float | None
    energy_total_kwh: float | None
    weather: dict[str, Any]
    bill: dict[str, Any]
    bill_items: dict[str, Any]
    bill_readings: dict[str, Any]
    imported_history_rows: int | None = None


class RiegEnergyApiClient:
    """Thin psycopg3 wrapper with retry, timeout and cache."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        ssl: bool,
        timezone: str,
        update_interval: int,
        consumer_unit: str | None = None,
    ) -> None:
        self.hass = hass
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.ssl = ssl
        self.timezone = timezone or DEFAULT_TIMEZONE
        self.update_interval = update_interval
        self.consumer_unit = consumer_unit
        self._connection: AsyncConnection | None = None
        self._cache: dict[str, tuple[datetime, Any]] = {}
        self._timings: list[float] = []
        self._query_count = 0
        self._row_count = 0
        self._last_error: str | None = None

    @classmethod
    def from_entry_data(cls, hass: HomeAssistant, entry: ConfigEntry) -> "RiegEnergyApiClient":
        """Build a client from config entry data."""
        data = entry.data
        return cls(
            hass,
            host=data[CONF_HOST],
            port=data.get(CONF_PORT, DEFAULT_PORT),
            database=data[CONF_DATABASE],
            username=data[CONF_USERNAME],
            password=data[CONF_PASSWORD],
            ssl=data.get(CONF_SSL, DEFAULT_SSL),
            timezone=data.get(CONF_TIMEZONE, DEFAULT_TIMEZONE),
            update_interval=data.get(CONF_UPDATE_INTERVAL, 300),
            consumer_unit=data.get(CONF_CONSUMER_UNIT),
        )

    @staticmethod
    async def validate_input(hass: HomeAssistant, data: Mapping[str, Any]) -> None:
        """Validate PostgreSQL credentials."""
        client = RiegEnergyApiClient(
            hass,
            host=data[CONF_HOST],
            port=data.get(CONF_PORT, DEFAULT_PORT),
            database=data[CONF_DATABASE],
            username=data[CONF_USERNAME],
            password=data[CONF_PASSWORD],
            ssl=data.get(CONF_SSL, DEFAULT_SSL),
            timezone=data.get(CONF_TIMEZONE, DEFAULT_TIMEZONE),
            update_interval=data.get(CONF_UPDATE_INTERVAL, 300),
        )
        try:
            await client.async_ensure_pool()
            await client.async_execute("SELECT 1", cache_key=None)
        except psycopg.Error as err:
            raise CannotConnect("postgres_error") from err
        except TimeoutError as err:
            raise CannotConnect("timeout") from err
        finally:
            await client.async_close()

    @staticmethod
    async def async_list_consumer_units(
        hass: HomeAssistant,
        data: Mapping[str, Any],
    ) -> list[str]:
        """Return available distinct consumer units from fatura."""
        client = RiegEnergyApiClient(
            hass,
            host=data[CONF_HOST],
            port=data.get(CONF_PORT, DEFAULT_PORT),
            database=data[CONF_DATABASE],
            username=data[CONF_USERNAME],
            password=data[CONF_PASSWORD],
            ssl=data.get(CONF_SSL, DEFAULT_SSL),
            timezone=data.get(CONF_TIMEZONE, DEFAULT_TIMEZONE),
            update_interval=data.get(CONF_UPDATE_INTERVAL, 300),
        )
        try:
            rows = await client.async_execute(
                """
                SELECT DISTINCT unidade_consumidora
                FROM fatura
                WHERE unidade_consumidora IS NOT NULL
                ORDER BY unidade_consumidora ASC
                """,
                cache_key=None,
            )
            units = [
                str(value).strip()
                for row in rows
                if (value := row.get("unidade_consumidora"))
                and str(value).strip()
            ]
            return units
        finally:
            await client.async_close()

    async def async_close(self) -> None:
        """Close the PostgreSQL connection."""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    def clear_cache(self) -> None:
        """Clear in-memory cache."""
        self._cache.clear()

    def get_runtime_stats(self) -> RuntimeStats:
        """Return runtime stats for diagnostics."""
        return RuntimeStats(
            query_count=self._query_count,
            row_count=self._row_count,
            last_error=self._last_error,
            average_query_time=fmean(self._timings) if self._timings else 0.0,
        )

    async def async_ensure_pool(self) -> AsyncConnection:
        """Create the psycopg3 connection on demand."""
        if self._connection is None:
            self._connection = await AsyncConnection.connect(
                host=self.host,
                port=self.port,
                dbname=self.database,
                user=self.username,
                password=self.password,
                sslmode="require" if self.ssl else "disable",
                connect_timeout=DEFAULT_TIMEOUT,
                row_factory=dict_row,
            )
        return self._connection

    async def async_execute(
        self,
        query: str,
        *args: Any,
        cache_key: str | None,
        cache_ttl: timedelta = QUERY_CACHE_TTL,
    ) -> list[dict[str, Any]]:
        """Execute a query with retry and cache support."""
        if cache_key:
            cached = self._cache.get(cache_key)
            now = dt_util.utcnow()
            if cached and now - cached[0] < cache_ttl:
                return cached[1]

        connection = await self.async_ensure_pool()
        delay = DEFAULT_RETRY_BASE
        last_err: Exception | None = None

        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                started = perf_counter()
                async with connection.cursor() as cursor:
                    await cursor.execute(query, args)
                    rows = await cursor.fetchall()
                elapsed = perf_counter() - started
                self._track_metric(QueryMetric(elapsed=elapsed, rows=len(rows)))
                if cache_key:
                    self._cache[cache_key] = (dt_util.utcnow(), rows)
                return rows
            except (psycopg.Error, TimeoutError) as err:
                last_err = err
                self._last_error = str(err)
                _LOGGER.warning(
                    "Query failed (attempt %s/%s): %s",
                    attempt + 1,
                    DEFAULT_RETRY_ATTEMPTS,
                    err,
                )
                await self.async_close()
                if attempt == DEFAULT_RETRY_ATTEMPTS - 1:
                    break
                await asyncio.sleep(delay)
                connection = await self.async_ensure_pool()
                delay *= 2

        assert last_err is not None
        raise last_err

    async def async_get_snapshot(self) -> AggregatedData:
        """Fetch a full normalized snapshot from PostgreSQL."""
        today = self._local_today()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        hourly_rows = await self.async_execute(
            """
            SELECT MAX(observed_at) AS observed_at, AVG(solar_power_w) AS solar_power_w
            FROM(
                SELECT 
                    complete_hour AS observed_at,
                    quantitty_producer::double precision AS solar_power_w
                FROM hourly_producer
                WHERE date_producer = CAST((CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo') AS DATE)
                AND (
                    hour_producer < EXTRACT(HOUR FROM CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    OR (
                        hour_producer = EXTRACT(HOUR FROM CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                        AND minute_producer <= EXTRACT(MINUTE FROM CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    )
                )
                ORDER BY complete_hour DESC, minute_producer DESC
                LIMIT 4
            )AS dataa
            """,
            cache_key="hourly_producer_latest",
        )
        monthly_rows = await self.async_execute(
            """
            SELECT
                date_producer::date AS observed_on,
                quantitty_producer::double precision AS energy_kwh
            FROM monthly_producer
            ORDER BY date_producer DESC
            """,
            cache_key="monthly_producer_all",
        )
        weather_rows = await self.async_execute(
            """
            SELECT *
            FROM meteoblue.solar_weather
            ORDER BY 1 DESC
            LIMIT 1
            """,
            cache_key="solar_weather_latest",
        )
        bill_cache_suffix = self.consumer_unit or "all"
        if self.consumer_unit:
            bill_query = """
                SELECT *
                FROM fatura
                WHERE unidade_consumidora = %s
                ORDER BY 1 DESC
                LIMIT 1
            """
            bill_args: tuple[Any, ...] = (self.consumer_unit,)
            bill_item_query = """
                WITH latest_bill AS (
                    SELECT id
                    FROM fatura
                    WHERE unidade_consumidora = %s
                    ORDER BY id DESC
                    LIMIT 1
                )
                SELECT fi.*
                FROM latest_bill lb
                JOIN fatura_item fi ON fi.id_fatura = lb.id
                ORDER BY fi.id DESC
            """
            bill_item_args: tuple[Any, ...] = (self.consumer_unit,)
            bill_reading_query = """
                WITH latest_bill AS (
                    SELECT id
                    FROM fatura
                    WHERE unidade_consumidora = %s
                    ORDER BY id DESC
                    LIMIT 1
                )
                SELECT fl.*
                FROM latest_bill lb
                JOIN fatura_leitura fl ON fl.id_fatura = lb.id
                ORDER BY fl.id DESC
            """
            bill_reading_args: tuple[Any, ...] = (self.consumer_unit,)
        else:
            # Backward compatibility for old entries created before consumer_unit became mandatory.
            bill_query = """
                SELECT *
                FROM fatura
                ORDER BY 1 DESC
                LIMIT 1
            """
            bill_args = ()
            bill_item_query = """
                WITH latest_bill AS (
                    SELECT id
                    FROM fatura
                    ORDER BY id DESC
                    LIMIT 1
                )
                SELECT fi.*
                FROM latest_bill lb
                JOIN fatura_item fi ON fi.id_fatura = lb.id
                ORDER BY fi.id DESC
            """
            bill_item_args = ()
            bill_reading_query = """
                WITH latest_bill AS (
                    SELECT id
                    FROM fatura
                    ORDER BY id DESC
                    LIMIT 1
                )
                SELECT fl.*
                FROM latest_bill lb
                JOIN fatura_leitura fl ON fl.id_fatura = lb.id
                ORDER BY fl.id DESC
            """
            bill_reading_args = ()

        bill_rows = await self.async_execute(
            bill_query,
            *bill_args,
            cache_key=f"bill_latest_{bill_cache_suffix}",
        )
        bill_item_rows = await self.async_execute(
            bill_item_query,
            *bill_item_args,
            cache_key=f"bill_items_latest_{bill_cache_suffix}",
        )
        bill_reading_rows = await self.async_execute(
            bill_reading_query,
            *bill_reading_args,
            cache_key=f"bill_readings_latest_{bill_cache_suffix}",
        )

        monthly = [self._normalize_monthly_row(row) for row in monthly_rows]
        energy_today = next(
            (row["energy_kwh"] for row in monthly if row["observed_on"] == today),
            None,
        )
        energy_week = self._sum_rows(monthly, start_of_week)
        energy_month = self._sum_rows(monthly, start_of_month)
        energy_year = self._sum_rows(monthly, start_of_year)
        energy_total = self._sum_rows(monthly, None)

        return AggregatedData(
            solar_power_w=(
                self._record_get(hourly_rows[0], "solar_power_w") if hourly_rows else None
            ),
            energy_today_kwh=energy_today,
            energy_week_kwh=energy_week,
            energy_month_kwh=energy_month,
            energy_year_kwh=energy_year,
            energy_total_kwh=energy_total,
            weather=self._normalize_weather(weather_rows[0]) if weather_rows else {},
            bill=self._normalize_bill(bill_rows[0]) if bill_rows else {},
            bill_items=self._normalize_bill_items(bill_item_rows, bill_rows[0] if bill_rows else None),
            bill_readings=self._normalize_bill_readings(bill_reading_rows),
            imported_history_rows=len(monthly),
        )

    async def async_get_monthly_history(
        self,
        *,
        start_date: date | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[dict[str, Any]]:
        """Return monthly producer rows normalized as daily history."""
        if start_date:
            rows = await self.async_execute(
                """
                SELECT
                    date_producer::date AS observed_on,
                    quantitty_producer::double precision AS energy_kwh
                FROM monthly_producer
                WHERE date_producer >= %s
                ORDER BY date_producer ASC
                LIMIT %s
                """,
                start_date,
                batch_size,
                cache_key=None,
            )
        else:
            rows = await self.async_execute(
                """
                SELECT
                    date_producer::date AS observed_on,
                    quantitty_producer::double precision AS energy_kwh
                FROM monthly_producer
                ORDER BY date_producer ASC
                LIMIT %s
                """,
                batch_size,
                cache_key=None,
            )
        return [self._normalize_monthly_row(row) for row in rows]

    def _track_metric(self, metric: QueryMetric) -> None:
        self._query_count += 1
        self._row_count += metric.rows
        self._timings.append(metric.elapsed)
        if len(self._timings) > 50:
            self._timings.pop(0)

    def _local_today(self) -> date:
        now = dt_util.now(dt_util.get_time_zone(self.timezone))
        return now.date()

    def _sum_rows(self, rows: list[dict[str, Any]], start_date: date | None) -> float | None:
        selected = (
            rows
            if start_date is None
            else [row for row in rows if row["observed_on"] >= start_date]
        )
        if not selected:
            return None
        return round(sum(row["energy_kwh"] for row in selected), 3)

    def _normalize_monthly_row(self, row: Mapping[str, Any]) -> dict[str, Any]:
        observed_on = self._record_get(row, "observed_on")
        if isinstance(observed_on, datetime):
            observed_on = observed_on.date()
        return {
            "observed_on": observed_on,
            "energy_kwh": self._to_float(self._record_get(row, "energy_kwh")),
        }

    def _normalize_weather(self, row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "forecast_generation": self._find_first_float(
                row,
                "forecast_generation",
                "previsao_geracao",
                "generation_forecast",
                "energy_forecast",
            ),
            "solar_radiation": self._find_first_float(
                row,
                "solar_radiation",
                "radiacao_solar",
                "radiation",
                "global_radiation",
                "directshortwaveradiation_total",
                "clearskyshortwave_total",
                "ghi_total",
            ),
            "cloud_cover": self._find_first_float(
                row,
                "cloud_cover",
                "cobertura_nuvens",
                "clouds",
                "totalcloudcover_mean",
                "totalcloudcover_max",
                "totalcloudcover_min",
            ),
            "sunshine_time": self._to_minutes(
                self._find_first_value(row, "sunshine_time", "sunshine", "sunshine_duration")
            ),
            "dni": self._find_first_float(row, "dni", "dni_total"),
            "ghi": self._find_first_float(row, "ghi", "ghi_total"),
            "dif": self._find_first_float(row, "dif", "dif_total"),
        }

    def _normalize_bill(self, row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "last_bill": self._find_first_float(
                row, "total_pagar", "valor", "last_bill", "total", "valor_total"
            ),
            "reference_month": self._find_first_value(
                row, "referencia", "mes_referencia", "reference_month", "competencia"
            ),
            "bill_due_date": self._find_first_value(
                row, "vencimento", "data_vencimento", "due_date", "bill_due_date"
            ),
        }

    def _normalize_bill_items(
        self,
        rows: list[Mapping[str, Any]],
        bill_row: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if not rows:
            return {}

        # Weighted average price from the latest bill items.
        quantity_total = 0.0
        value_total = 0.0
        energy_te = 0.0
        energy_tusd = 0.0
        injected_value = 0.0
        consumed_value = 0.0
        has_energy_te = False
        has_energy_tusd = False
        has_injected = False
        has_consumed = False

        for row in rows:
            description = str(self._find_first_value(row, "descricao_item") or "").lower()
            quantity = self._find_first_float(row, "quantidade")
            value = self._find_first_float(row, "valor")

            if quantity is not None and value is not None and quantity > 0:
                quantity_total += quantity
                value_total += value

            if quantity is not None and "tusd" in description:
                energy_tusd += quantity
                has_energy_tusd = True
            elif quantity is not None and " te" in f" {description} ":
                energy_te += quantity
                has_energy_te = True

            if value is not None and ("injet" in description or "compens" in description):
                injected_value += abs(value)
                has_injected = True
            elif value is not None and "consum" in description:
                consumed_value += value
                has_consumed = True

        average_price = round(value_total / quantity_total, 3) if quantity_total > 0 else None
        tariff_flag = self._find_first_value(
            rows[0],
            "bandeira_tarifaria",
            "tariff_flag",
            "flag",
        )
        if tariff_flag is None and bill_row is not None:
            tariff_flag = self._find_first_value(
                bill_row,
                "modalidade_tarifaria",
                "classificacao",
            )

        return {
            "average_price": average_price
            if average_price is not None
            else self._find_first_float(rows[0], "preco_medio_kwh", "average_price", "valor_medio_kwh"),
            "energy_te": round(energy_te, 3)
            if has_energy_te
            else self._find_first_float(rows[0], "energia_te", "energy_te", "te"),
            "energy_tusd": round(energy_tusd, 3)
            if has_energy_tusd
            else self._find_first_float(rows[0], "energia_tusd", "energy_tusd", "tusd"),
            "tariff_flag": tariff_flag,
            "injected_value": round(injected_value, 3)
            if has_injected
            else self._find_first_float(rows[0], "valor_injetado", "injected_value", "credito_injetado"),
            "consumed_value": round(consumed_value, 3)
            if has_consumed
            else self._find_first_float(rows[0], "valor_consumido", "consumed_value", "custo_consumido"),
        }

    def _normalize_bill_readings(self, rows: list[Mapping[str, Any]]) -> dict[str, Any]:
        if not rows:
            return {}

        latest_row = rows[0]
        previous_reading = self._find_first_float(latest_row, "leitura_anterior", "previous_reading")
        current_reading = self._find_first_float(latest_row, "leitura_atual", "current_reading")
        diff = None
        if previous_reading is not None and current_reading is not None:
            diff = round(current_reading - previous_reading, 3)

        energy_consumed = 0.0
        energy_injected = 0.0
        has_consumed = False
        has_injected = False

        for row in rows:
            total_apurado = self._find_first_float(row, "total_apurado")
            grandeza = str(self._find_first_value(row, "grandeza") or "").lower()

            if total_apurado is None:
                continue

            if "injet" in grandeza or total_apurado < 0:
                energy_injected += abs(total_apurado)
                has_injected = True
            else:
                energy_consumed += total_apurado
                has_consumed = True

        return {
            "energy_consumed": round(energy_consumed, 3)
            if has_consumed
            else self._find_first_float(
                latest_row, "energia_consumida", "energy_consumed", "consumed_energy"
            ),
            "energy_injected": round(energy_injected, 3)
            if has_injected
            else self._find_first_float(
                latest_row, "energia_injetada", "energy_injected", "injected_energy"
            ),
            "previous_reading": previous_reading,
            "current_reading": current_reading,
            "reading_difference": diff,
        }

    def _record_get(self, row: Mapping[str, Any], key: str) -> Any:
        return row[key]

    def _find_first_value(self, row: Mapping[str, Any], *keys: str) -> Any:
        mapping = dict(row)
        lowered = {str(key).lower(): value for key, value in mapping.items()}
        for key in keys:
            if key in mapping:
                return mapping[key]
            if key.lower() in lowered:
                return lowered[key.lower()]
        return None

    def _find_first_float(self, row: Mapping[str, Any], *keys: str) -> float | None:
        value = self._find_first_value(row, *keys)
        return self._to_float(value)

    def _to_float(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            return round(float(value), 3)
        except (TypeError, ValueError):
            return None

    def _to_minutes(self, value: Any) -> float | None:
        """Convert supported time-like values into minutes."""
        if value is None:
            return None

        if isinstance(value, timedelta):
            return round(value.total_seconds() / 60, 3)

        if isinstance(value, datetime):
            value = value.time()

        if isinstance(value, time):
            seconds = value.hour * 3600 + value.minute * 60 + value.second
            return round(seconds / 60, 3)

        if isinstance(value, str):
            try:
                parsed = time.fromisoformat(value)
            except ValueError:
                return self._to_float(value)
            seconds = parsed.hour * 3600 + parsed.minute * 60 + parsed.second
            return round(seconds / 60, 3)

        return self._to_float(value)
