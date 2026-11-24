"""Binary sensors of WAFE heat recovery units."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from wafe_modbus import WafeUnit

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import WafeConfigEntry
from .entity import WafeEntity, WafeEntityDescription

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class WafeBinarySensorEntityDescription(
    BinarySensorEntityDescription, WafeEntityDescription
):
    """Describe a WAFE binary sensor."""

    value_fn: Callable[[WafeUnit], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[WafeBinarySensorEntityDescription, ...] = (
    WafeBinarySensorEntityDescription(
        key="bypass",
        translation_key="bypass",
        component="status",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.status.bypass_active,
    ),
    WafeBinarySensorEntityDescription(
        key="holiday_ventilation",
        translation_key="holiday_ventilation",
        component="status",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.status.holiday_ventilation_active,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WafeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the WAFE binary sensors."""
    async_add_entities(
        WafeBinarySensor(entry.runtime_data, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class WafeBinarySensor(WafeEntity, BinarySensorEntity):
    """A binary sensor of a WAFE unit."""

    entity_description: WafeBinarySensorEntityDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return whether the condition holds."""
        return self.entity_description.value_fn(self.device)
