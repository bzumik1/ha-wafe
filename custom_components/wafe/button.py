"""Buttons of WAFE heat recovery units."""

from dataclasses import dataclass
from typing import override

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import WafeConfigEntry
from .entity import WafeEntity, WafeEntityDescription

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class WafeButtonEntityDescription(ButtonEntityDescription, WafeEntityDescription):
    """Describe a WAFE button."""


LONG_BOOST = WafeButtonEntityDescription(
    key="long_boost",
    translation_key="long_boost",
    component="functions",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WafeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the WAFE buttons."""
    async_add_entities([WafeLongBoostButton(entry.runtime_data, LONG_BOOST)])


class WafeLongBoostButton(WafeEntity, ButtonEntity):
    """Start the long boost of a WAFE unit."""

    entity_description: WafeButtonEntityDescription

    @override
    async def async_press(self) -> None:
        """Start the long boost."""
        await self._async_write(
            lambda: self.device.functions.async_start_boost(long=True)
        )
