"""Diagnostics support for WAFE heat recovery units."""

from typing import Any

from modbus_connection import ModbusError

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .coordinator import WafeConfigEntry

TO_REDACT = {CONF_HOST}
# The unit's ID in the vendor cloud, which is also the config entry's unique ID.
UNIT_ID_REGISTER = 1000


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: WafeConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry, with the raw register map."""
    coordinator = entry.runtime_data
    device = coordinator.device
    raw: dict[str, Any] | None = None
    read_error: str | None = None
    try:
        raw = await device.async_read_raw()
    except ModbusError as err:
        read_error = type(err).__name__
    else:
        del raw["input"][UNIT_ID_REGISTER]

    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "model": device.model.name if device.model is not None else None,
        "updated": sorted(coordinator.data.updated),
        "failed": {name: str(err) for name, err in coordinator.data.failed.items()},
        "read_error": read_error,
        "registers": raw,
    }
