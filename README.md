# WAFE for Home Assistant

A Home Assistant integration for WAFE heat recovery ventilation units with the ACE2 controller, such as the WAFE 201 E. It talks to the unit over Modbus TCP on your local network. No cloud account is needed.

This repository is the preview of the WAFE integration that is being contributed to Home Assistant Core. Once the full integration is part of a Home Assistant release, remove this custom integration and use the built-in one; the entities keep their IDs.

The device communication lives in the [`wafe-modbus`](https://github.com/bzumik1/wafe-modbus) library.

## Requirements

- Home Assistant 2026.11 or newer.
- The unit is connected to your network with an Ethernet cable, and has a fixed IP address in your router.
- No other Modbus client is connected to the unit. The unit serves only one Modbus client at a time. If you read the unit with a `modbus:` entry in your YAML configuration, remove that entry and restart Home Assistant first.

## Installation

1. In HACS, open the three-dot menu, choose **Custom repositories**, and add `https://github.com/bzumik1/ha-wafe` with the type **Integration**.
2. Search for **WAFE** in HACS and download it.
3. Restart Home Assistant.
4. Go to **Settings** > **Devices & services**, select **Add integration**, search for **WAFE**, and enter the unit's IP address. The Modbus port is `502` by default.

## Entities

### Sensors

- **Outdoor**, **Supply**, **Extract** and **Exhaust temperature** (T1 to T4).
- **Carbon dioxide** of the extracted room air.
- **Target airflow**: The airflow the unit currently aims for. The unit does not measure the airflow it delivers.
- **Fan 1 speed** and **Fan 2 speed**, in rpm. The unit refreshes them about every 30 seconds.
- **State**: Ventilation, manual, standby or holiday.

### Controls

- **Operating mode** (select): Intelligent (follows CO2), manual, scheduler (follows the weekly plan from the MyWAFE app; without a plan the fans stop) or ultra-saving.
- **Boost** (switch): On while a boost runs. Turning it on starts a short boost; turning it off ends any boost.
- **Long boost** (button): Starts the long boost.
- **Holiday mode**, **Silent mode** and **Standby** (switches).
- **Manual airflow**, **CO2 setpoint**, **Short boost duration** and **Long boost duration** (numbers).

### Disabled by default

These are normally set once by the installer. Enable them from the entity settings if you need them.

- **Fireplace mode** (has no effect until the installer enables it on the unit).
- **Bypass** (binary sensor), **Block bypass**, **Bypass airflow by CO2**, and the bypass airflow, months and temperature differences. On the tested WAFE 201 E the bypass did not open, so not every unit may have one.
- **Airflow limit**, **Minimum**, **Maximum** and **Limited maximum airflow**.
- **Fan imbalance** (had no effect on the tested unit) and **Preheater start temperature**.
- **Holiday ventilation** (diagnostic binary sensor).

## Data updates

The integration reads the whole unit every 5 seconds, which takes three short Modbus requests. Home Assistant only records a state when a value changes. A change made in the MyWAFE app shows up within 5 seconds of the unit applying it; the unit itself takes 10 to 25 seconds to receive it from the cloud.

## Known limitations

- The MyWAFE app keeps its own copy of the manual airflow, so after a change from Home Assistant the app can show the old value.
- Filter status, error messages and the weekly plan are not available over Modbus.

## License

Apache-2.0
