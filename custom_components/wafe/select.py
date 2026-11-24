"""Operating mode select of WAFE heat recovery units."""

from dataclasses import dataclass
from typing import override

from wafe_modbus import OperatingMode

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import WafeConfigEntry
from .entity import WafeEntity, WafeEntityDescription

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class WafeSelectEntityDescription(SelectEntityDescription, WafeEntityDescription):
    """Describe a WAFE select."""


OPERATING_MODE = WafeSelectEntityDescription(
    key="operating_mode",
    translation_key="operating_mode",
    component="functions",
    options=[mode.name.lower() for mode in OperatingMode],
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WafeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the WAFE select."""
    async_add_entities([WafeOperatingModeSelect(entry.runtime_data, OPERATING_MODE)])


class WafeOperatingModeSelect(WafeEntity, SelectEntity):
    """Select the operating mode of a WAFE unit."""

    entity_description: WafeSelectEntityDescription

    @property
    @override
    def current_option(self) -> str | None:
        """Return the mode whose coil is set."""
        mode = self.device.functions.operating_mode
        return mode.name.lower() if mode is not None else None

    @override
    async def async_select_option(self, option: str) -> None:
        """Switch the unit to the selected mode."""
        mode = OperatingMode[option.upper()]
        await self._async_write(lambda: self.device.async_set_operating_mode(mode))
