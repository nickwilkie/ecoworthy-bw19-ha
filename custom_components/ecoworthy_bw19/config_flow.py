"""Discover or manually add an ECO-WORTHY BW19 inverter."""

import re

import voluptuous as vol

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from . import DOMAIN
from .protocol import SERVICE_UUID

_ADDRESS = re.compile(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}")


def _is_bw19(info: bluetooth.BluetoothServiceInfoBleak) -> bool:
    return info.name.upper().startswith("ECO-WORTHY 19_") and (
        SERVICE_UUID in info.service_uuids
    )


class BW19ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up one config entry per Bluetooth address."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        errors = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip().upper()
            if not _ADDRESS.fullmatch(address):
                errors[CONF_ADDRESS] = "invalid_address"
            else:
                info = bluetooth.async_last_service_info(
                    self.hass, address, connectable=True
                )
                if info is None:
                    errors["base"] = "not_found"
                elif not _is_bw19(info):
                    errors["base"] = "unsupported"
                else:
                    await self.async_set_unique_id(address)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=info.name, data={CONF_ADDRESS: address}
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): str}),
            errors=errors,
        )

    async def async_step_bluetooth(
        self, discovery_info: bluetooth.BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        if not _is_bw19(discovery_info):
            return self.async_abort(reason="unsupported")

        self._discovery = discovery_info
        await self.async_set_unique_id(discovery_info.address.upper())
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery.name,
                data={CONF_ADDRESS: self._discovery.address.upper()},
            )
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"name": self._discovery.name},
        )
