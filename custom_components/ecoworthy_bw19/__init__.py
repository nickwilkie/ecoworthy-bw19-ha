"""Home Assistant integration for ECO-WORTHY BW19 inverter telemetry."""

from datetime import timedelta
import logging

from bleak.exc import BleakError

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import async_read_status
from .protocol import Status

DOMAIN = "ecoworthy_bw19"
_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

type BW19ConfigEntry = ConfigEntry[BW19Coordinator]


class BW19Coordinator(DataUpdateCoordinator[Status]):
    """Use a single Bluetooth poll to update all three measurements."""

    def __init__(self, hass: HomeAssistant, entry: BW19ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
            always_update=False,
        )
        self.address = entry.data[CONF_ADDRESS]

    async def _async_update_data(self) -> Status:
        device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if device is None:
            raise UpdateFailed("No active Bluetooth adapter can see the inverter")

        try:
            return await async_read_status(device)
        except (BleakError, OSError, TimeoutError) as err:
            raise UpdateFailed(f"BW19 status request failed: {err or type(err).__name__}") from err


async def async_setup_entry(hass: HomeAssistant, entry: BW19ConfigEntry) -> bool:
    """Set up an inverter after receiving the first valid sample."""
    coordinator = BW19Coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BW19ConfigEntry) -> bool:
    """Unload the inverter's entities."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
