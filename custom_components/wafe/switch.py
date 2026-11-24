"""Switches of WAFE heat recovery units."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, override

from wafe_modbus import WafeUnit

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import WafeConfigEntry
from .entity import WafeEntity, WafeEntityDescription

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class WafeSwitchEntityDescription(SwitchEntityDescription, WafeEntityDescription):
    """Describe a WAFE switch."""

    value_fn: Callable[[WafeUnit], bool | None]
    write_fn: Callable[[WafeUnit, bool], Awaitable[None]]


def _function(key: str, *, enabled: bool = True) -> WafeSwitchEntityDescription:
    return WafeSwitchEntityDescription(
        key=key,
        translation_key=key,
        component="functions",
        entity_registry_enabled_default=enabled,
        value_fn=lambda device: getattr(device.functions, key),
        write_fn=lambda device, value: device.functions.write(key, value),
    )


def _setting(key: str) -> WafeSwitchEntityDescription:
    return WafeSwitchEntityDescription(
        key=key,
        translation_key=key,
        component="settings",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        value_fn=lambda device: getattr(device.settings, key),
        write_fn=lambda device, value: device.settings.write(key, value),
    )


async def _set_boost(device: WafeUnit, value: bool) -> None:
    if value:
        await device.functions.async_start_boost()
    else:
        await device.functions.async_stop_boost()


SWITCH_DESCRIPTIONS: tuple[WafeSwitchEntityDescription, ...] = (
    WafeSwitchEntityDescription(
        key="boost",
        translation_key="boost",
        component="functions",
        value_fn=lambda device: device.functions.boost_active,
        write_fn=_set_boost,
    ),
    _function("holiday"),
    _function("silent"),
    _function("standby"),
    _function("fireplace", enabled=False),
    WafeSwitchEntityDescription(
        key="block_bypass",
        translation_key="block_bypass",
        component="functions",
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.functions.bypass_off,
        write_fn=lambda device, value: device.functions.write("bypass_off", value),
    ),
    _setting("bypass_by_co2"),
    _setting("airflow_limit"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WafeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the WAFE switches."""
    async_add_entities(
        WafeSwitch(entry.runtime_data, description)
        for description in SWITCH_DESCRIPTIONS
    )


class WafeSwitch(WafeEntity, SwitchEntity):
    """A switch of a WAFE unit."""

    entity_description: WafeSwitchEntityDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return the state the unit reported."""
        return self.entity_description.value_fn(self.device)

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the function on."""
        await self._async_write(
            lambda: self.entity_description.write_fn(self.device, True)
        )

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the function off."""
        await self._async_write(
            lambda: self.entity_description.write_fn(self.device, False)
        )
