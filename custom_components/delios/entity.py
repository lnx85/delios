"""Delios inverter entities."""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum
from typing import Any, Optional

from attr import dataclass
from .client import (
    AlarmsData,
    StatusData,
    FirmwareData,
    SensorsData,
    ParametersData,
)
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
    inverter: Optional[DeliosInverter] = None
    key: Optional[str] = None
    name: Optional[str] = None
    state_class: Optional[str] = None
    device_class: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    suggested_display_precision: Optional[int] = None
    value: Callable[[Any], Any] = lambda v: v
    attributes: dict[str, Callable[[Any], Any]] = {}
    integration: bool = False


class HelperFilterRangeType(Enum):
    """Helper filter range type."""

    NEGATIVE = -1
    POSITIVE = 1


@dataclass
class HelperFilterEntity:
    """Helper entity."""

    name: Optional[str] = None
    entity_id: Optional[str] = None
    range: Optional[HelperFilterRangeType] = None
    type: Optional[DeliosEntityType] = None


SENSORS: list[DeliosInverterAttribute] = [
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_power",
        name="Battery Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            float(data["sensors"].get("PowerBatt"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_charge_power",
        name="Battery Charge Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            max(0.0, -float(data["sensors"].get("PowerBatt")))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_discharge_power",
        name="Battery Discharge Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            max(0.0, float(data["sensors"].get("PowerBatt")))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_charge_energy_total",
        name="Battery Charge Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        integration=True,
        value=lambda data: (
            max(0.0, -float(data["sensors"].get("PowerBatt")) * 1000)
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_discharge_energy_total",
        name="Battery Discharge Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        integration=True,
        value=lambda data: (
            max(0.0, float(data["sensors"].get("PowerBatt")) * 1000)
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_power",
        name="Grid Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            float(data["sensors"].get("PowerGrid"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="photovoltaic_power",
        name="Photovoltaic Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            float(data["sensors"].get("PowerPV"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="house_power",
        name="House Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            float(data["sensors"].get("PowerHouse"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    # Instantaneous power flows mirroring the energy totals (buyed / injected /
    # self-consumed). The Delios API only exposes a single signed grid power
    # (PowerGrid), so these split it by direction and derive self-consumption.
    # Sign convention (verified on an IBRIDO DLS unit against live data):
    #   PowerGrid > 0 = power drawn from the grid (buyed / import)
    #   PowerGrid < 0 = power fed into the grid (injected / export)
    # Self-consumed = the share of PV production not exported to the grid.
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="buyed_power",
        name="Buyed Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            max(0.0, float(data["sensors"].get("PowerGrid")))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="injected_power",
        name="Injected Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            max(0.0, -float(data["sensors"].get("PowerGrid")))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="self_consumed_power",
        name="Self Consumed Power",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value=lambda data: (
            max(
                0.0,
                float(data["sensors"].get("PowerPV"))
                - max(0.0, -float(data["sensors"].get("PowerGrid"))),
            )
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    # Real-time energy totals, integrated from the instantaneous power flows above.
    # These REPLACE the former TotalizerData-based *_energy_total sensors: the Delios
    # /info/totalizer endpoint only commits its cumulative counters once per day at the
    # inverter's local midnight, and the inverter clock stays on standard time (it does
    # not follow DST). On the HA Energy dashboard a whole day's energy therefore landed
    # in a single 01:00 bucket (00:00 in winter) and was attributed to the wrong day.
    # Integrating the live power instead yields correctly time-bucketed, DST-correct
    # energy. The running total is a RestoreSensor, so it persists across restarts.
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="photovoltaic_energy_total",
        name="Photovoltaic Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        integration=True,
        value=lambda data: (
            float(data["sensors"].get("PowerPV")) * 1000
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="buyed_energy_total",
        name="Buyed Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        integration=True,
        value=lambda data: (
            max(0.0, float(data["sensors"].get("PowerGrid")) * 1000)
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="injected_energy_total",
        name="Injected Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        integration=True,
        value=lambda data: (
            max(0.0, -float(data["sensors"].get("PowerGrid")) * 1000)
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="self_consumed_energy_total",
        name="Self Consumed Energy Total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        integration=True,
        value=lambda data: (
            max(
                0.0,
                (
                    float(data["sensors"].get("PowerPV"))
                    - max(0.0, -float(data["sensors"].get("PowerGrid")))
                )
                * 1000,
            )
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_percent",
        name="Battery Percent",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        unit_of_measurement=PERCENTAGE,
        value=lambda data: (
            float(data["sensors"].get("PercentBattery"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_current",
        name="Grid Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: (
            float(data["sensors"].get("IL1"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_voltage",
        name="Grid Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: (
            float(data["sensors"].get("VL1"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_1_current",
        name="String 1 Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: (
            float(data["sensors"].get("IS1"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_1_voltage",
        name="String 1 Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: (
            float(data["sensors"].get("VS1"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_2_current",
        name="String 2 Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: (
            float(data["sensors"].get("IS2"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="string_2_voltage",
        name="String 2 Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: (
            float(data["sensors"].get("VS2"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_current",
        name="Battery Current",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value=lambda data: (
            float(data["sensors"].get("IBatt"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_voltage",
        name="Battery Voltage",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value=lambda data: (
            float(data["sensors"].get("VBatt"))
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="inverter_alarm",
        name="Inverter Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value=lambda data: (
            int(data["sensors"].get("InvAlarm")) != 0
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="photovoltaic_alarm",
        name="Photovoltaic Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value=lambda data: (
            int(data["sensors"].get("PVAlarm")) != 0
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="battery_alarm",
        name="Battery Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value=lambda data: (
            int(data["sensors"].get("BattAlarm")) != 0
            if isinstance(data, dict)
            and "sensors" in data
            and isinstance(data["sensors"], SensorsData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="inverter_temperature",
        name="Inverter Temperature",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value=lambda data: (
            float(data["parameters"].get("ACinvTemp"))
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_temperature",
        name="Battery Temperature",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value=lambda data: (
            float(data["parameters"].get("BatteryTemp"))
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="r_iso_pv1",
        name="R iso PV1",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement="KOhm",
        value=lambda data: (
            float(data["parameters"].get("Riso1"))
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="r_iso_pv2",
        name="R iso PV2",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement="KOhm",
        value=lambda data: (
            float(data["parameters"].get("Riso2"))
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="r_iso_com",
        name="R iso Com",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement="KOhm",
        value=lambda data: (
            float(data["parameters"].get("RisoM"))
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="i_diff",
        name="I Diff",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        value=lambda data: (
            float(data["parameters"].get("IDiff"))
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="i_diff_test",
        name="I Diff Test",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        value=lambda data: (
            float(data["parameters"].get("IDiffTest"))
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="li_ion_info",
        name="Li-ION Info",
        value=lambda data: (
            int(data["parameters"].get("InfoLiIonBatt")) != 0
            if isinstance(data, dict)
            and "parameters" in data
            and isinstance(data["parameters"], ParametersData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="last_alarm",
        name="Last alarm",
        value=lambda data: (
            data["alarms"].last_alarm_code
            if isinstance(data, dict)
            and "alarms" in data
            and isinstance(data["alarms"], AlarmsData)
            else None
        ),
        attributes={
            "description": lambda data: (
                data["alarms"].last_alarm_description
                if isinstance(data, dict)
                and "alarms" in data
                and isinstance(data["alarms"], AlarmsData)
                else None
            ),
            "alarm_date": lambda data: (
                data["alarms"].last_alarm_date
                if isinstance(data, dict)
                and "alarms" in data
                and isinstance(data["alarms"], AlarmsData)
                else None
            ),
        },
    ),
]

SETTINGS: list[DeliosEntityType] = [
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="usb",
        name="USB",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value=lambda data: (
            data["status"].usb
            if isinstance(data, dict)
            and "status" in data
            and isinstance(data["status"], StatusData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="lan",
        name="LAN",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value=lambda data: (
            data["status"].lan
            if isinstance(data, dict)
            and "status" in data
            and isinstance(data["status"], StatusData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.BINARY_SENSOR,
        key="wifi",
        name="Wi-Fi",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value=lambda data: (
            data["status"].wifi
            if isinstance(data, dict)
            and "status" in data
            and isinstance(data["status"], StatusData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="machine_firmware",
        name="Machine Firmware",
        value=lambda data: (
            data["firmware"].machine
            if isinstance(data, dict)
            and "firmware" in data
            and isinstance(data["firmware"], FirmwareData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="grid_firmware",
        name="Grid Firmware",
        value=lambda data: (
            data["firmware"].grid
            if isinstance(data, dict)
            and "firmware" in data
            and isinstance(data["firmware"], FirmwareData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="photovoltaic_firmware",
        name="Photovoltaic Firmware",
        value=lambda data: (
            data["firmware"].photovoltaic
            if isinstance(data, dict)
            and "firmware" in data
            and isinstance(data["firmware"], FirmwareData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="battery_firmware",
        name="Battery Firmware",
        value=lambda data: (
            data["firmware"].battery
            if isinstance(data, dict)
            and "firmware" in data
            and isinstance(data["firmware"], FirmwareData)
            else None
        ),
    ),
    DeliosInverterAttribute(
        type=DeliosEntityType.SENSOR,
        key="inverter_firmware",
        name="Inverter Firmware",
        value=lambda data: (
            data["firmware"].firmware
            if isinstance(data, dict)
            and "firmware" in data
            and isinstance(data["firmware"], FirmwareData)
            else None
        ),
    ),
]
