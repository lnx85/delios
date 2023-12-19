"""Delios inverter sensors."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DeliosSensorsCoordinator, DeliosSystemCoordinator
from .entity import DeliosEntityType
from .inverter import inverter_from_data

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add binary sensors for passed config_entry in HA."""
    inverter = inverter_from_data(config_entry.data)
    hass.data.setdefault(DOMAIN, {})
    if not inverter.unique_id in hass.data[DOMAIN]:
        hass.data[DOMAIN][inverter.unique_id] = {}
    if not BINARY_SENSOR_DOMAIN in hass.data[DOMAIN][inverter.unique_id]:
        hass.data[DOMAIN][inverter.unique_id][BINARY_SENSOR_DOMAIN] = {}
    sensors_coordinator = DeliosSensorsCoordinator(hass, inverter)
    await sensors_coordinator.setup()
    await sensors_coordinator.async_config_entry_first_refresh()
    sensors_coordinator.add_entities(async_add_entities, DeliosEntityType.BINARY_SENSOR)
    system_coordinator = DeliosSystemCoordinator(hass, inverter)
    await system_coordinator.setup()
    await system_coordinator.async_config_entry_first_refresh()
    system_coordinator.add_entities(async_add_entities, DeliosEntityType.BINARY_SENSOR)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Unload binary sensors for passed config_entry in HA."""
    await hass.config_entries.async_forward_entry_unload(
        config_entry, BINARY_SENSOR_DOMAIN
    )
