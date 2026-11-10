"""Request a single status sample using Home Assistant's BLE device."""

import asyncio
from contextlib import suppress

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection

from .protocol import (
    COMMAND_UUID,
    NOTIFY_UUID,
    SERVICE_UUID,
    STATUS_REQUEST,
    Status,
    StatusDecoder,
)


async def async_read_status(device: BLEDevice) -> Status:
    """Connect, collect one valid sample, and release the Bluetooth slot."""
    decoder = StatusDecoder(device.address)
    sample = asyncio.get_running_loop().create_future()

    def notification(
        _characteristic: BleakGATTCharacteristic, payload: bytearray
    ) -> None:
        if not sample.done() and (status := decoder.feed(payload)) is not None:
            sample.set_result(status)

    async with asyncio.timeout(25):
        client = await establish_connection(
            BleakClient, device, "ECO-WORTHY BW19", max_attempts=2
        )
    try:
        async with asyncio.timeout(10):
            service = client.services.get_service(SERVICE_UUID)
            if service is None:
                raise BleakError("BW19 status service is missing")

            rx = service.get_characteristic(NOTIFY_UUID)
            tx = service.get_characteristic(COMMAND_UUID)
            if rx is None or tx is None:
                raise BleakError("BW19 status characteristics are missing")

            await client.start_notify(rx, notification)
            await client.write_gatt_char(tx, STATUS_REQUEST, response=True)
            return await sample
    finally:
        sample.cancel()
        with suppress(BleakError, TimeoutError):
            async with asyncio.timeout(6):
                await client.disconnect()
