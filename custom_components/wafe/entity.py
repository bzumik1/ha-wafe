"""Base entity for WAFE heat recovery units."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from modbus_connection import ModbusConnectionError, ModbusError, ModbusTimeoutError
from wafe_modbus import WafeUnit

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WafeDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class WafeEntityDescription(EntityDescription):
    """Describe a WAFE entity."""

    component: str
    """Attribute name of the library component the entity reads."""


class WafeEntity(CoordinatorEntity[WafeDataUpdateCoordinator]):
    """An entity of a WAFE unit."""

    _attr_has_entity_name = True
    entity_description: WafeEntityDescription

    def __init__(
        self,
        coordinator: WafeDataUpdateCoordinator,
        entity_description: WafeEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        if TYPE_CHECKING:
            assert coordinator.config_entry.unique_id is not None
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_{entity_description.key}"
        )
        self._attr_device_info = coordinator.device_info

    @property
    def device(self) -> WafeUnit:
        """The library object of the unit."""
        return self.coordinator.device

    @property
    @override
    def available(self) -> bool:
        """Whether this entity's component answered the latest poll."""
        return (
            super().available
            and self.entity_description.component in self.coordinator.data.updated
        )

    async def _async_write(self, write: Callable[[], Awaitable[None]]) -> None:
        """Write to the unit, then read it back so the entities show the result."""
        try:
            await write()
        except ValueError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_value",
            ) from err
        except (ModbusConnectionError, ModbusTimeoutError) as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="unit_unreachable",
            ) from err
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
            ) from err
        await self.coordinator.async_refresh()
