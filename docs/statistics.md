# Statistics

## Overview

The integration imports solar production history into Home Assistant using the official statistics API.

It does not write directly to the Home Assistant database.

## Implementation

- Source table: `monthly_producer`
- API: `async_add_external_statistics`
- Progress persistence: `homeassistant.helpers.storage.Store`

## Supported Operations

- Full import
- Incremental import
- Resume after interruption
- Rebuild imported statistics
- Batch processing

## Services

- `rieg_energy.import_history`
- `rieg_energy.rebuild_statistics`

## Limitations

The historical import currently targets production history only. Consumption, injection, and additional Energy Dashboard statistics remain future work.
