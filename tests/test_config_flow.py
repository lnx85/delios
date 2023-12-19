"""Tests for the config flow."""
from unittest.mock import ANY, patch

import pytest
import voluptuous as vol
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.delios.const import (
    CONF_HOST,
    CONF_MODEL,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
)


@pytest.fixture(autouse=True)
# pylint: disable=unused-argument
def auto_enable_custom_integrations(enable_custom_integrations):
    """Auto enable custom integrations."""
    yield


@pytest.fixture
def bypass_setup():
    """Prevent actual setup of the integration after config flow."""
    with patch(
        "custom_components.delios.async_setup_entry",
        return_value=True,
    ):
        yield


@pytest.mark.asyncio
async def test_init_entry(hass):
    """Test initialization of the config flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        title="test",
        data={
            CONF_NAME: "test",
            CONF_MODEL: "IBRIDO DLS",
            CONF_HOST: "localhost",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "user",
            CONF_SCAN_INTERVAL: 10,
        },
        options={},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


@pytest.mark.asyncio
async def test_flow_user_init(hass):
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    expected = {
        "data_schema": ANY,
        "description_placeholders": None,
        "errors": {},
        "flow_id": ANY,
        "handler": DOMAIN,
        "step_id": "user",
        "type": "form",
        "last_step": ANY,
        "preview": ANY,
    }
    assert expected == result
    # Check the schema.  Simple comparison does not work since they are not
    # the same object
    try:
        result["data_schema"](
            {
                CONF_NAME: "test",
                CONF_MODEL: "IBRIDO DLS",
                CONF_HOST: "localhost",
                CONF_USERNAME: "user",
                CONF_PASSWORD: "user",
                CONF_SCAN_INTERVAL: 10,
            }
        )
    except vol.MultipleInvalid:
        assert False
    try:
        result["data_schema"]({CONF_NAME: "missing_some"})
        assert False
    except vol.MultipleInvalid:
        pass
