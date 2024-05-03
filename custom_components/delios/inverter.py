"""Delios inverter class."""

from __future__ import annotations

import hashlib
import logging

from attr import dataclass

from .const import (
    CONF_HOST,
    CONF_MODEL,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeliosInverter:
    """Delios inverter manager."""

    name: str = ""
    model: str = ""
    host: str = ""
    username: str = ""
    password: str = ""
    scan_interval: int = 10
    helper_entities: bool = False

    @property
    def unique_id(self) -> str:
        """Inverter unique ID."""
        return hashlib.sha1(self.name.encode()).hexdigest()


def inverter_from_data(data: dict) -> DeliosInverter:
    """Return an inverter object from dict data."""
    return DeliosInverter(
        name=data[CONF_NAME],
        model=data[CONF_MODEL],
        host=data[CONF_HOST],
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        scan_interval=data[CONF_SCAN_INTERVAL],
    )
