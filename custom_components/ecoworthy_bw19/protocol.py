"""Decode the BW19 inverter's Bluetooth status notifications."""

from dataclasses import dataclass
from struct import unpack_from

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
COMMAND_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

# This is the request the vendor app uses to resume status notifications
# after reconnecting, with the clock fields blank.
STATUS_REQUEST = bytes.fromhex(
    "ff 08 02 00 11 01 00 32 00 ff ff ff ff ff ff ff 46 1f 00 14 ff ff 87 36"
)
STATUS_ACK = bytes.fromhex("ff 08 00 46 30")
STATUS_HEADER = bytes.fromhex("f7 7f 02 01 01 38")
STATUS_SIZE = 68


@dataclass(frozen=True)
class Status:
    """Measurements verified against the vendor app."""

    battery_voltage: float
    battery_current: float
    ac_voltage: float


def _crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


class StatusDecoder:
    """Assemble split notifications and verify status frames."""

    def __init__(self, address: str) -> None:
        self._address = bytes.fromhex(address.replace(":", ""))
        self._buffer = bytearray()

    def feed(self, data: bytes | bytearray) -> Status | None:
        """Return the next valid status frame, if any."""
        if data == STATUS_ACK:
            return None

        self._buffer.extend(data)
        while True:
            start = self._buffer.find(STATUS_HEADER)
            if start == -1:
                # A header can begin at the end of one notification.
                self._buffer = self._buffer[-(len(STATUS_HEADER) - 1):]
                return None

            del self._buffer[:start]
            if len(self._buffer) < STATUS_SIZE:
                return None

            frame = bytes(self._buffer[:STATUS_SIZE])
            if (
                frame[6:12] == self._address
                and frame[15:17] == b"\x01\xa1"
                and frame[-2:] == b"\x5a\xa5"
                and int.from_bytes(frame[60:62], "little")
                == _crc16_modbus(frame[3:60])
            ):
                del self._buffer[:STATUS_SIZE]
                voltage, current, ac_voltage = unpack_from(">HhH", frame, 24)
                return Status(voltage / 10, current / 10, ac_voltage / 10)

            # A lost notification can put a new frame inside the candidate.
            del self._buffer[0]
