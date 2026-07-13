# FAQ

## Why does the integration not talk to Growatt?

Because the project specification requires PostgreSQL to be the single source of truth.

## Does the integration write to PostgreSQL?

No. It only reads data.

## Does the integration write directly to Home Assistant recorder tables?

No. Historical imports use official Home Assistant statistics APIs only.

## Why are some bill and weather fields alias-based?

Because the specification defines the expected sensors but does not lock every physical column name for those tables.

## Why are some Energy Dashboard features still missing?

The current implementation covers solar production history. Full consumption and injection modeling still need to be implemented.
