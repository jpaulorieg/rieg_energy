# PostgreSQL

## Supported Tables

- `hourly_producer`
- `monthly_producer`
- `meteoblue.solar_weather`
- `fatura`
- `fatura_item`
- `fatura_leitura`

## Expectations

- The integration is read-only.
- PostgreSQL access is asynchronous through `psycopg3`.
- The integration assumes the tables already exist and are populated by an external pipeline.

## Notes About Column Names

`hourly_producer` and `monthly_producer` have explicit field mappings in the specification.

Some tables in the specification define expected sensors but not every physical column name. For those cases, the integration normalizes values through alias-based lookup in `custom_components/rieg_energy/api.py`.

If your schema diverges from those aliases, update the mappings before deployment.

For `meteoblue.solar_weather`, the integration supports these column mappings out of the box:

- `sensor.solar_radiation`: `directshortwaveradiation_total`, `clearskyshortwave_total`, `ghi_total` (fallback aliases also supported)
- `sensor.cloud_cover`: `totalcloudcover_mean` (fallback to `totalcloudcover_max`/`totalcloudcover_min` and aliases)
- `sensor.sunshine_time`: `sunshine_time` (`time` converted to minutes)
- `sensor.dni`: `dni_total`
- `sensor.ghi`: `ghi_total`
- `sensor.dif`: `dif_total`

`sensor.forecast_generation` remains alias-based because this value is not explicitly defined in the `solar_weather` DDL above.

For billing tables, the integration expects these mappings:

- `fatura.unidade_consumidora`: selected during config flow and used as filter key for billing queries.
- `sensor.last_bill`: `fatura.total_pagar`
- `sensor.reference_month`: `fatura.referencia`
- `sensor.bill_due_date`: `fatura.vencimento`
- `sensor.average_price`: weighted average from `fatura_item.valor / fatura_item.quantidade` on the latest bill.
- `sensor.energy_te`: sum of `fatura_item.quantidade` for rows whose `descricao_item` identifies TE.
- `sensor.energy_tusd`: sum of `fatura_item.quantidade` for rows whose `descricao_item` identifies TUSD.
- `sensor.tariff_flag`: `fatura.modalidade_tarifaria` (fallback for legacy aliases).
- `sensor.injected_value`: sum of absolute `fatura_item.valor` for rows whose `descricao_item` identifies injection/compensation.
- `sensor.consumed_value`: sum of `fatura_item.valor` for rows whose `descricao_item` identifies consumption.
- `sensor.energy_consumed` / `sensor.energy_injected`: aggregated from `fatura_leitura.total_apurado` (positive consumed, negative or injected grandeza as injected).
- `sensor.previous_reading` / `sensor.current_reading`: from the most recent `fatura_leitura` row of the latest bill.

Query strategy for FK integrity:

- Determine the latest bill row from `fatura` using `ORDER BY id DESC LIMIT 1` with `WHERE unidade_consumidora = ?`.
- Load `fatura_item` only through `JOIN fatura_item ON fatura_item.id_fatura = fatura.id`.
- Load `fatura_leitura` only through `JOIN fatura_leitura ON fatura_leitura.id_fatura = fatura.id`.

## Performance

- Connections are pooled.
- Queries are executed directly against PostgreSQL on every refresh.
- Retries use exponential backoff.
- Timeouts are enforced on PostgreSQL calls.
