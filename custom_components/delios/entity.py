"""Delios inverter entities."""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum
from typing import Any

from attr import dataclass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
)

from .inverter import DeliosInverter

_LOGGER = logging.getLogger(__name__)


class DeliosEntityType(Enum):
    """Delios inverter attribute type."""

    SENSOR = 1
    BINARY_SENSOR = 2


@dataclass
class DeliosInverterAttribute:
    """Delios inverter attribute."""

    type: DeliosEntityType = DeliosEntityType.SENSOR
    inverter: DeliosInverter = None
    key: str = None
    name: str = None
    state_class: str = None
    device_class: str = None
    unit_of_measurement: str = None
    value: Callable[[Any], Any] = lambda v: v


class HelperFilterRangeType(Enum):
    """Helper filter range type."""

    NEGATIVE = -1
    POSITIVE = 1


@dataclass
class HelperFilterEntity:
    """Helper entity."""

    name: str = None
    entity_id: str = None
    range: HelperFilterRangeType = None
    type: DeliosEntityType = None


SENSORS: list[DeliosInverterAttribute] = [
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_power",
        name="Battery Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.WATT,
        value=lambda data: float(data["sensors"].get("PowerBatt")) * 1000,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_power",
        name="Grid Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.WATT,
        value=lambda data: float(data["sensors"].get("PowerGrid")) * 1000,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="photovoltaic_power",
        name="Photovoltaic Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.WATT,
        value=lambda data: float(data["sensors"].get("PowerPV")) * 1000,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="house_power",
        name="House Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.WATT,
        value=lambda data: float(data["sensors"].get("PowerHouse")) * 1000,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_percent",
        name="Battery Percent",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        unit_of_measurement=PERCENTAGE,
        value=lambda data: float(data["sensors"].get("PercentBattery")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_current",
        name="Grid Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: float(data["sensors"].get("IL1")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_voltage",
        name="Grid Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: float(data["sensors"].get("VL1")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_1_current",
        name="String 1 Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: float(data["sensors"].get("IS1")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_1_voltage",
        name="String 1 Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: float(data["sensors"].get("VS1")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_2_current",
        name="String 2 Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: float(data["sensors"].get("IS2")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_2_voltage",
        name="String 2 Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: float(data["sensors"].get("VS2")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_current",
        name="Battery Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: float(data["sensors"].get("IBatt")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_voltage",
        name="Battery Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: float(data["sensors"].get("VBatt")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="inverter_alarm",
        name="Inverter Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value=lambda data: int(data["sensors"].get("InvAlarm")) != 0,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="photovoltaic_alarm",
        name="Photovoltaic Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value=lambda data: int(data["sensors"].get("PVAlarm")) != 0,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="battery_alarm",
        name="Battery Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value=lambda data: int(data["sensors"].get("BattAlarm")) != 0,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="inverter_temperature",
        name="Inverter Temperature",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value=lambda data: float(data["parameters"].get("ACinvTemp")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_temperature",
        name="Battery Temperature",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value=lambda data: float(data["parameters"].get("BatteryTemp")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="r_iso_pv1",
        name="R iso PV1",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement="KOhm",
        value=lambda data: float(data["parameters"].get("Riso1")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="r_iso_pv2",
        name="R iso PV2",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement="KOhm",
        value=lambda data: float(data["parameters"].get("Riso2")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="r_iso_com",
        name="R iso Com",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement="KOhm",
        value=lambda data: float(data["parameters"].get("RisoM")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="i_diff",
        name="I Diff",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        value=lambda data: float(data["parameters"].get("IDiff")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="i_diff_test",
        name="I Diff Test",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        value=lambda data: float(data["parameters"].get("IDiffTest")),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="li_ion_info",
        name="Li-ION Info",
        value=lambda data: int(data["parameters"].get("InfoLiIonBatt")) != 0,
    ),
]

SETTINGS: list[DeliosEntityType] = [
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="usb",
        name="USB",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value=lambda data: data["status"].usb,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="lan",
        name="LAN",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value=lambda data: data["status"].lan,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="wifi",
        name="Wi-Fi",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value=lambda data: data["status"].wifi,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="machine_firmware",
        name="Machine Firmware",
        value=lambda data: data["firmware"].machine,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_firmware",
        name="Grid Firmware",
        value=lambda data: data["firmware"].grid,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="photovoltaic_firmware",
        name="Photovoltaic Firmware",
        value=lambda data: data["firmware"].photovoltaic,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_firmware",
        name="Battery Firmware",
        value=lambda data: data["firmware"].battery,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="inverter_firmware",
        name="Inverter Firmware",
        value=lambda data: data["firmware"].firmware,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="photovoltaic_energy_total",
        name="Photovoltaic Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value=lambda data: data["totalizer"].photovoltaic,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_energy_total",
        name="Buyed Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value=lambda data: data["totalizer"].buyed,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="injected_energy_total",
        name="Injected Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value=lambda data: data["totalizer"].injected,
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="self_consumed_energy_total",
        name="Self Consumed Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value=lambda data: data["totalizer"].self_consumed,
    ),
]
