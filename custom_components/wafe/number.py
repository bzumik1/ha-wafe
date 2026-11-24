"""Number settings of WAFE heat recovery units."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import override

from wafe_modbus import WafeUnit

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfRatio,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import WafeConfigEntry
from .entity import WafeEntity, WafeEntityDescription

PARALLEL_UPDATES = 1

M3H = UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR


@dataclass(frozen=True, kw_only=True)
class WafeNumberEntityDescription(NumberEntityDescription, WafeEntityDescription):
    """Describe a number backed by a holding register."""

    value_fn: Callable[[WafeUnit], float | None]
    set_fn: Callable[[WafeUnit, float], Awaitable[None]]
    min_fn: Callable[[WafeUnit], float | None] | None = None
    max_fn: Callable[[WafeUnit], float | None] | None = None


def _airflow(key: str) -> WafeNumberEntityDescription:
    return WafeNumberEntityDescription(
        key=key,
        translation_key=key,
        component="settings",
        value_fn=lambda device: getattr(device.settings, key),
        set_fn=lambda device, value: device.settings.write(key, value),
        device_class=NumberDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=M3H,
        native_min_value=0,
        native_max_value=1000,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    )


def _month(key: str) -> WafeNumberEntityDescription:
    return WafeNumberEntityDescription(
        key=key,
        translation_key=key,
        component="settings",
        value_fn=lambda device: getattr(device.settings, key),
        set_fn=lambda device, value: device.settings.write(key, value),
        native_min_value=1,
        native_max_value=12,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    )


def _temperature_difference(key: str) -> WafeNumberEntityDescription:
    return WafeNumberEntityDescription(
        key=key,
        translation_key=key,
        component="settings",
        value_fn=lambda device: getattr(device.settings, key),
        set_fn=lambda device, value: device.settings.write(key, value),
        device_class=NumberDeviceClass.TEMPERATURE_DELTA,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0,
        native_max_value=20,
        native_step=0.1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    )


def _boost_duration(key: str) -> WafeNumberEntityDescription:
    return WafeNumberEntityDescription(
        key=key,
        translation_key=key,
        component="settings",
        value_fn=lambda device: getattr(device.settings, key),
        set_fn=lambda device, value: device.settings.write(key, value),
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=60,
        native_max_value=14400,
        native_step=60,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    )


NUMBER_DESCRIPTIONS: tuple[WafeNumberEntityDescription, ...] = (
    WafeNumberEntityDescription(
        key="manual_airflow",
        translation_key="manual_airflow",
        component="settings",
        value_fn=lambda device: device.settings.manual_airflow,
        device_class=NumberDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=M3H,
        native_step=1,
        mode=NumberMode.SLIDER,
        min_fn=lambda device: device.settings.min_airflow,
        max_fn=lambda device: device.settings.max_airflow,
        set_fn=lambda device, value: device.async_set_manual_airflow(int(value)),
    ),
    WafeNumberEntityDescription(
        key="co2_setpoint",
        translation_key="co2_setpoint",
        component="settings",
        value_fn=lambda device: device.settings.co2_setpoint,
        set_fn=lambda device, value: device.settings.write("co2_setpoint", value),
        device_class=NumberDeviceClass.CO2,
        native_unit_of_measurement=UnitOfRatio.PARTS_PER_MILLION,
        native_min_value=400,
        native_max_value=2000,
        native_step=10,
        mode=NumberMode.BOX,
    ),
    _airflow("min_airflow"),
    _airflow("max_airflow"),
    _airflow("limited_max_airflow"),
    _boost_duration("short_boost_duration"),
    _boost_duration("long_boost_duration"),
    WafeNumberEntityDescription(
        key="fan_imbalance",
        translation_key="fan_imbalance",
        component="settings",
        value_fn=lambda device: device.settings.fan_imbalance,
        set_fn=lambda device, value: device.settings.write("fan_imbalance", value),
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=-100,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    _airflow("bypass_airflow"),
    _month("bypass_start_month"),
    _month("bypass_end_month"),
    _temperature_difference("bypass_min_temperature_difference"),
    _temperature_difference("night_bypass_min_temperature_difference"),
    WafeNumberEntityDescription(
        key="preheat_start_temperature",
        translation_key="preheat_start_temperature",
        component="settings",
        value_fn=lambda device: device.settings.preheat_start_temperature,
        set_fn=lambda device, value: device.settings.write(
            "preheat_start_temperature", value
        ),
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-20,
        native_max_value=5,
        native_step=0.5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WafeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the WAFE numbers."""
    async_add_entities(
        WafeNumber(entry.runtime_data, description)
        for description in NUMBER_DESCRIPTIONS
    )


class WafeNumber(WafeEntity, NumberEntity):
    """A numeric setting of a WAFE unit."""

    entity_description: WafeNumberEntityDescription

    @property
    @override
    def native_value(self) -> float | None:
        """Return the value the unit reported."""
        return self.entity_description.value_fn(self.device)

    @property
    @override
    def native_min_value(self) -> float:
        """Return the lowest value the unit accepts."""
        if (min_fn := self.entity_description.min_fn) is not None and (
            value := min_fn(self.device)
        ) is not None:
            return value
        return super().native_min_value

    @property
    @override
    def native_max_value(self) -> float:
        """Return the highest value the unit accepts."""
        if (max_fn := self.entity_description.max_fn) is not None and (
            value := max_fn(self.device)
        ) is not None:
            return value
        return super().native_max_value

    @override
    async def async_set_native_value(self, value: float) -> None:
        """Write the value to the unit."""
        await self._async_write(
            lambda: self.entity_description.set_fn(self.device, value)
        )
