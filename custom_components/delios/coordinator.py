"""Delios coordinator."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import slugify

from .client import DeliosClient, UnauthorizedClient
from .const import DOMAIN, SYSTEM_UPDATE_INTERVAL
from .entity import SENSORS, SETTINGS, DeliosEntityType, DeliosInverterAttribute
from .inverter import DeliosInverter

_LOGGER = logging.getLogger(__name__)

ENTITY_ID_SENSOR_FORMAT = SENSOR_DOMAIN + ".{}_{}"
ENTITY_ID_BINARY_SENSOR_FORMAT = BINARY_SENSOR_DOMAIN + ".{}_{}"


class DeliosBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Delios inverter binary sensor."""

    def __init__(
        self, coordinator: DeliosCoordinator, attribute: DeliosInverterAttribute
    ) -> None:
        """Initializebinary sensor."""

        super().__init__(coordinator, context=attribute)
        self._attribute = attribute
        inverter = self.coordinator.inverter
        self.entity_id = ENTITY_ID_BINARY_SENSOR_FORMAT.format(
            slugify(inverter.name), attribute.key
        )
        self.entity_description = BinarySensorEntityDescription(
            key=attribute.key,
            name=attribute.name,
            device_class=attribute.device_class,
        )
        self._attr_unique_id = f"{inverter.unique_id}-{attribute.key}"
        self._attr_device_info = DeviceInfo(
            name=inverter.name,
            identifiers={(DOMAIN, inverter.unique_id)},
            manufacturer="Delios",
            model=inverter.model,
        )
        if self.coordinator.data:
            self._attr_is_on = self._attribute.value(self.coordinator.data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        try:
            self._attr_is_on = self._attribute.value(self.coordinator.data)
            self.async_write_ha_state()
        except KeyError:
            pass


class DeliosSensor(CoordinatorEntity, SensorEntity):
    """Delios inverter sensor."""

    def __init__(
        self, coordinator: DeliosCoordinator, attribute: DeliosInverterAttribute
    ) -> None:
        """Initialize sensor."""

        super().__init__(coordinator, context=attribute)
        self._attribute = attribute
        self._internal_value = None
        inverter = self.coordinator.inverter
        self.entity_id = ENTITY_ID_SENSOR_FORMAT.format(
            slugify(inverter.name), attribute.key
        )
        self.entity_description = SensorEntityDescription(
            key=attribute.key,
            name=attribute.name,
            state_class=attribute.state_class,
            device_class=attribute.device_class,
            native_unit_of_measurement=attribute.unit_of_measurement,
            suggested_display_precision=attribute.suggested_display_precision,
        )
        self._attr_unique_id = f"{inverter.unique_id}-{attribute.key}"
        self._attr_device_info = DeviceInfo(
            name=inverter.name,
            identifiers={(DOMAIN, inverter.unique_id)},
            manufacturer="Delios",
            model=inverter.model,
        )
        if self.coordinator.data:
            self._internal_value = self._attribute.value(self.coordinator.data)

    @property
    def native_value(self) -> str | int | None:
        """Return value of sensor."""

        return self._internal_value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        try:
            self._internal_value = self._attribute.value(self.coordinator.data)
            self.async_write_ha_state()
        except KeyError:
            pass


class DeliosCoordinator(DataUpdateCoordinator):
    """Delios coordinator."""

    def __init__(self, hass: HomeAssistant, inverter: DeliosInverter) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Delios",
            update_interval=timedelta(seconds=inverter.scan_interval),
        )
        self._inverter = inverter
        self._client = None

    @property
    def inverter(self) -> DeliosInverter:
        """Return inverter."""
        return self._inverter

    @property
    def entities(self) -> list[DeliosSensor]:
        """Return coordinator entities."""
        return []

    async def setup(self) -> None:
        """Configure coordinator client."""
        self._client = DeliosClient(self.hass, self._inverter.host)
        await self._client.login(self._inverter.username, self._inverter.password)

    def add_entities(
        self,
        async_add_entities: AddEntitiesCallback,
        attribute_type: DeliosEntityType,
    ) -> None:
        """Add entities."""
        if self.entities:
            entities = []
            for entity in self.entities:
                if entity.type == attribute_type:
                    if entity.type == DeliosEntityType.SENSOR:
                        self.hass.data[DOMAIN][self._inverter.unique_id][SENSOR_DOMAIN][
                            entity.key
                        ] = DeliosSensor(self, entity)
                        entities.append(
                            self.hass.data[DOMAIN][self._inverter.unique_id][
                                SENSOR_DOMAIN
                            ][entity.key]
                        )
                    elif entity.type == DeliosEntityType.BINARY_SENSOR:
                        self.hass.data[DOMAIN][self._inverter.unique_id][
                            BINARY_SENSOR_DOMAIN
                        ][entity.key] = DeliosBinarySensor(self, entity)
                        entities.append(
                            self.hass.data[DOMAIN][self._inverter.unique_id][
                                BINARY_SENSOR_DOMAIN
                            ][entity.key]
                        )
            async_add_entities(entities)


class DeliosSensorsCoordinator(DeliosCoordinator):
    """Sensors coordinator."""

    @property
    def entities(self) -> list[DeliosSensor]:
        """Return coordinator entities."""
        return SENSORS

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            return {
                "sensors": await self._client.sensors(),
                "parameters": await self._client.parameters(),
            }
        except UnauthorizedClient as exception:
            _LOGGER.error("Unable to retreive sensors data: %s", str(exception))


class DeliosSystemCoordinator(DeliosCoordinator):
    """System coordinator."""

    def __init__(self, hass: HomeAssistant, inverter: DeliosInverter) -> None:
        """Initialize System coordinator."""
        super().__init__(hass, inverter)
        self.update_interval = timedelta(seconds=SYSTEM_UPDATE_INTERVAL)

    @property
    def entities(self) -> list[DeliosSensor]:
        """Return coordinator entities."""
        return SETTINGS

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            return {
                "status": await self._client.status(),
                "totalizer": await self._client.totalizer(),
                "firmware": await self._client.firmware(),
            }
        except UnauthorizedClient as exception:
            _LOGGER.error("Unable to retreive sensors data: %s", str(exception))
