"""Delios coordinator."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .client import DeliosClient, InvalidAttribute, UnauthorizedClient
from .const import DOMAIN, SYSTEM_UPDATE_INTERVAL
from .entity import SENSORS, SETTINGS, DeliosEntityType, DeliosInverterAttribute
from .inverter import DeliosInverter

_LOGGER = logging.getLogger(__name__)

ENTITY_ID_SENSOR_FORMAT = SENSOR_DOMAIN + ".{}_{}"
ENTITY_ID_BINARY_SENSOR_FORMAT = BINARY_SENSOR_DOMAIN + ".{}_{}"

# Errors raised while evaluating an attribute value when the underlying inverter
# data is missing or not yet available (e.g. an endpoint returned no variables for
# this hardware). Such an attribute is treated as "value unavailable" rather than
# being allowed to crash entity setup or a coordinator update.
VALUE_UNAVAILABLE_ERRORS = (KeyError, TypeError, ValueError, InvalidAttribute)


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
        self._attr_is_on = None
        self._internal_attributes = {}
        if self.coordinator.data:
            try:
                self._attr_is_on = self._attribute.value(self.coordinator.data)
                self._internal_attributes = {
                    attribute: value(self.coordinator.data)
                    for attribute, value in self._attribute.attributes.items()
                }
            except VALUE_UNAVAILABLE_ERRORS:
                pass

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return attributes of sensor."""

        return self._internal_attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        try:
            self._attr_is_on = self._attribute.value(self.coordinator.data)
            self._internal_attributes = {
                attribute: value(self.coordinator.data)
                for attribute, value in self._attribute.attributes.items()
            }
            self.async_write_ha_state()
        except VALUE_UNAVAILABLE_ERRORS:
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
        self._internal_attributes = {}
        if self.coordinator.data:
            try:
                self._internal_value = self._attribute.value(self.coordinator.data)
                self._internal_attributes = {
                    attribute: value(self.coordinator.data)
                    for attribute, value in self._attribute.attributes.items()
                }
            except VALUE_UNAVAILABLE_ERRORS:
                pass

    @property
    def native_value(self) -> str | int | None:
        """Return value of sensor."""

        return self._internal_value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return attributes of sensor."""

        return self._internal_attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        try:
            self._internal_value = self._attribute.value(self.coordinator.data)
            self._internal_attributes = {
                attribute: value(self.coordinator.data)
                for attribute, value in self._attribute.attributes.items()
            }
            self.async_write_ha_state()
        except VALUE_UNAVAILABLE_ERRORS:
            pass


class DeliosIntegrationSensor(CoordinatorEntity, RestoreSensor):
    """Delios energy sensor computed by integrating an instantaneous power value over time.

    The Delios API only exposes the instantaneous battery power, not cumulative
    charge/discharge energy. This sensor integrates the power (in watts) returned
    by the attribute over time to produce a kWh total that can be used in the Home
    Assistant Energy dashboard. The running total is restored across restarts.
    """

    def __init__(
        self, coordinator: DeliosCoordinator, attribute: DeliosInverterAttribute
    ) -> None:
        """Initialize integration sensor."""

        super().__init__(coordinator, context=attribute)
        self._attribute = attribute
        self._state: float = 0.0
        self._last_power: float | None = None
        self._last_update: datetime | None = None
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

    @property
    def native_value(self) -> float:
        """Return the accumulated energy."""

        return self._state

    async def async_added_to_hass(self) -> None:
        """Restore the last accumulated value and seed the integration baseline."""

        await super().async_added_to_hass()
        last_data = await self.async_get_last_sensor_data()
        if last_data is not None and last_data.native_value is not None:
            try:
                self._state = float(last_data.native_value)
            except (TypeError, ValueError):
                self._state = 0.0
        self._integrate()

    def _current_power(self) -> float | None:
        """Return the instantaneous power (in watts) to integrate."""

        try:
            return self._attribute.value(self.coordinator.data)
        except VALUE_UNAVAILABLE_ERRORS:
            return None

    def _integrate(self) -> None:
        """Accumulate energy using the trapezoidal rule between two power readings."""

        now = dt_util.utcnow()
        power = self._current_power()
        if (
            power is not None
            and self._last_power is not None
            and self._last_update is not None
        ):
            elapsed = (now - self._last_update).total_seconds()
            if elapsed > 0:
                average_power = (power + self._last_power) / 2
                # W * s -> Wh (/3600) -> kWh (/1000)
                self._state += average_power * elapsed / 3600 / 1000
        if power is not None:
            self._last_power = power
            self._last_update = now

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._integrate()
        self.async_write_ha_state()


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
                        sensor = (
                            DeliosIntegrationSensor(self, entity)
                            if entity.integration
                            else DeliosSensor(self, entity)
                        )
                        self.hass.data[DOMAIN][self._inverter.unique_id][SENSOR_DOMAIN][
                            entity.key
                        ] = sensor
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
        data: dict[str, Any] = {
            "sensors": None,
            "parameters": None,
            "alarms": None,
        }
        # sensors
        try:
            data["sensors"] = await self._client.sensors()
        except UnauthorizedClient:
            _LOGGER.error("Unable to retreive sensors data")
        # parameters
        try:
            data["parameters"] = await self._client.parameters()
        except UnauthorizedClient:
            _LOGGER.error("Unable to retreive parameters data")
        # alarms
        try:
            data["alarms"] = await self._client.alarms()
        except UnauthorizedClient:
            _LOGGER.error("Unable to retreive alarms data")
        # return
        return data


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
        data: dict[str, Any] = {
            "status": None,
            "alarms": None,
        }
        # status
        try:
            data["status"] = await self._client.status()
        except UnauthorizedClient:
            _LOGGER.error("Unable to retreive status data")
        # firmware
        try:
            data["firmware"] = await self._client.firmware()
        except UnauthorizedClient:
            _LOGGER.error("Unable to retreive firmware data")
        # return
        return data
