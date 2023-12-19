"""Tests for the sensor entity."""
from unittest.mock import Mock

import pytest
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
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
from custom_components.delios.coordinator import DeliosSensor
from custom_components.delios.sensor import async_setup_entry


@pytest.mark.asyncio
async def test_init_entry(hass):
    """Test the initialization."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "test",
            CONF_MODEL: "IBRIDO DLS",
            CONF_HOST: "localhost",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "user",
            CONF_SCAN_INTERVAL: 10,
        },
    )
    m_add_entities = Mock()
    await async_setup_entry(hass, entry, m_add_entities)
    assert isinstance(
        hass.data[DOMAIN]["a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"][SENSOR_DOMAIN][
            "battery_percent"
        ],
        DeliosSensor,
    )
