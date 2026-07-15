"""Tests for the Delios client data parsing."""

import pytest

from custom_components.delios.client import (
    InvalidAttribute,
    ParametersData,
    SensorsData,
)


def test_sensors_data_parses_variable_list():
    """A normal dashboard payload is parsed into ctrl_name -> value."""
    data = SensorsData(
        {"variables": [{"ctrl_name": "VL1", "value": "251.5"}]}
    )
    assert data.get("VL1") == 251.5


def test_sensors_data_null_variables_does_not_crash():
    """A payload with `variables: null` must not raise (regression).

    Some inverters / firmware return {"variables": null} for an endpoint;
    iterating over None previously raised TypeError and broke the whole
    coordinator update.
    """
    data = SensorsData({"variables": None})
    with pytest.raises(InvalidAttribute):
        data.get("VL1")


def test_parameters_data_null_variables_does_not_crash():
    """`info/system` returns {"variables": null} on some hardware (regression).

    The parameters endpoint can legitimately have no variables; parsing it
    must yield an empty, queryable object instead of raising TypeError.
    """
    params = ParametersData({"variables": None})
    with pytest.raises(InvalidAttribute):
        params.get("ACinvTemp")


def test_parameters_data_missing_key_returns_invalid_attribute():
    """Reading an absent ctrl_name raises InvalidAttribute, not KeyError."""
    params = ParametersData({"variables": []})
    with pytest.raises(InvalidAttribute):
        params.get("ACinvTemp")
