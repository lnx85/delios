"""Delios inverter sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
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
    """Add sensors for passed config_entry in HA."""
    inverter = inverter_from_data(config_entry.data)
    hass.data.setdefault(DOMAIN, {})
    if inverter.unique_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][inverter.unique_id] = {}
    if SENSOR_DOMAIN not in hass.data[DOMAIN][inverter.unique_id]:
        hass.data[DOMAIN][inverter.unique_id][SENSOR_DOMAIN] = {}
    sensors_coordinator = DeliosSensorsCoordinator(hass, inverter)
    await sensors_coordinator.setup()
    await sensors_coordinator.async_config_entry_first_refresh()
    sensors_coordinator.add_entities(async_add_entities, DeliosEntityType.SENSOR)
    system_coordinator = DeliosSystemCoordinator(hass, inverter)
    await system_coordinator.setup()
    await system_coordinator.async_config_entry_first_refresh()
    system_coordinator.add_entities(async_add_entities, DeliosEntityType.SENSOR)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Unload sensors for passed config_entry in HA."""
    await hass.config_entries.async_forward_entry_unload(config_entry, SENSOR_DOMAIN)
