"""Measurement entities for the ECO-WORTHY BW19 inverter."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, BW19ConfigEntry, BW19Coordinator

_SENSORS = (
    SensorEntityDescription(
        key="battery_voltage",
        name="Battery voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SensorEntityDescription(
        key="battery_current",
        name="Battery current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    SensorEntityDescription(
        key="ac_voltage",
        name="AC voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BW19ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the inverter's three measurement entities."""
    async_add_entities(
        BW19Sensor(entry.runtime_data, entry.title, description)
        for description in _SENSORS
    )


class BW19Sensor(CoordinatorEntity[BW19Coordinator], SensorEntity):
    """Report one value from a validated status sample."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(
        self, coordinator: BW19Coordinator, name: str, description: SensorEntityDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
            connections={(CONNECTION_BLUETOOTH, coordinator.address)},
            manufacturer="ECO-WORTHY",
            model="BW19",
            name=name,
        )

    @property
    def native_value(self) -> float:
        return getattr(self.coordinator.data, self.entity_description.key)
