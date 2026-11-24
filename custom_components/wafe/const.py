"""Constants for the WAFE integration."""

from datetime import timedelta

DOMAIN = "wafe"
MANUFACTURER = "WAFE"

DEFAULT_PORT = 502
# The controller ignores the unit ID, so it is not asked for.
UNIT_ID = 1

# The manual airflow sits among the settings and is changed in the vendor app, so
# everything is polled at the same pace: three requests on the local network.
SCAN_INTERVAL = timedelta(seconds=5)
