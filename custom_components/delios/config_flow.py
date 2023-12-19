"""Config flow."""

from __future__ import annotations

import hashlib
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.core import callback

from .client import DeliosClient
from .const import (
    CONF_HOST,
    CONF_MODEL,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    MODELS,
)

_LOGGER = logging.getLogger(__name__)


class DeliosConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Delios config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    device = None
    data = {}

    async def async_step_user(self, user_input=None):
        """User config flow."""
        errors = {}
        name_opts = {}
        model_opts = {}
        host_opts = {}
        username_opts = {"default": DEFAULT_USERNAME}
        password_opts = {}
        scan_interval_opts = {"default": DEFAULT_SCAN_INTERVAL}
        if user_input is not None:
            name_opts["default"] = user_input[CONF_NAME]
            model_opts["default"] = user_input[CONF_MODEL]
            host_opts["default"] = user_input[CONF_HOST]
            username_opts["default"] = user_input[CONF_USERNAME]
            password_opts["default"] = user_input[CONF_PASSWORD]
            scan_interval_opts["default"] = int(user_input[CONF_SCAN_INTERVAL])
            if len(user_input[CONF_NAME]) < 3:
                errors[CONF_NAME] = "name_too_short"
            delios = DeliosClient(self.hass, user_input[CONF_HOST])
            if await delios.validate() is not True:
                errors[CONF_HOST] = "invalid_device"
            elif (
                await delios.login(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
                is not True
            ):
                errors[CONF_USERNAME] = "invalid_username"
                errors[CONF_PASSWORD] = "invalid_password"
            elif int(user_input[CONF_SCAN_INTERVAL] < 0):
                errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"
            else:
                unique_id = hashlib.sha1(user_input[CONF_NAME].encode()).hexdigest()
                await self.async_set_unique_id(unique_id)
                user_input["unique_id"] = unique_id
                self._abort_if_unique_id_configured({CONF_HOST: user_input[CONF_HOST]})
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, **name_opts): cv.string,
                    vol.Required(CONF_MODEL, **model_opts): vol.In(MODELS),
                    vol.Required(CONF_HOST, **host_opts): cv.string,
                    vol.Required(CONF_USERNAME, **username_opts): cv.string,
                    vol.Required(CONF_PASSWORD, **password_opts): cv.string,
                    vol.Required(
                        CONF_SCAN_INTERVAL, **scan_interval_opts
                    ): cv.positive_int,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Delios options flow."""

    def __init__(self, config_entry):
        """Delios options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Start options flow."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Manage the options."""
        errors = {}
        config = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            config = {**config, **user_input}
            delios = DeliosClient(self.hass, config.get(CONF_HOST, ""))
            if await delios.validate() is not True:
                errors[CONF_HOST] = "invalid_device"
            elif (
                await delios.login(
                    config.get(CONF_USERNAME, ""), config.get(CONF_PASSWORD, "")
                )
                is not True
            ):
                errors[CONF_USERNAME] = "invalid_username"
                errors[CONF_PASSWORD] = "invalid_password"
            elif int(user_input[CONF_SCAN_INTERVAL] < 0):
                errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"
            else:
                return self.async_create_entry(
                    title=config.get(CONF_NAME, ""), data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=config.get(CONF_HOST, "")
                    ): cv.string,
                    vol.Required(
                        CONF_USERNAME, default=config.get(CONF_USERNAME, "")
                    ): cv.string,
                    vol.Required(
                        CONF_PASSWORD, default=config.get(CONF_PASSWORD, "")
                    ): cv.string,
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=config.get(CONF_SCAN_INTERVAL, 10)
                    ): cv.positive_int,
                }
            ),
            errors=errors,
        )
