# Installation

## Manual Installation

1. Copy `custom_components/rieg_energy` to your Home Assistant config directory under `custom_components/`.
2. Restart Home Assistant.
3. Open `Settings > Devices & Services > Add Integration`.
4. Search for `Rieg Energy`.
5. Fill in the PostgreSQL connection settings.

## HACS Installation

1. Open HACS.
2. Add this repository as a custom integration repository.
3. Install `Rieg Energy`.
4. Restart Home Assistant.
5. Configure the integration from the UI.

## Required Inputs

- PostgreSQL host
- PostgreSQL port
- Database name
- Username
- Password
- SSL enabled or disabled
- Update interval in seconds
- Timezone
- Consumer unit (`unidade_consumidora`) selected from table `fatura`
