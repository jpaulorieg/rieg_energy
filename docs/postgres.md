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

## Performance

- Connections are pooled.
- Queries are cached in memory when appropriate.
- Retries use exponential backoff.
- Timeouts are enforced on PostgreSQL calls.
