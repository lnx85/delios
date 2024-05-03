"""Client implementation for Delios Web Server."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import aiohttp
from attr import dataclass
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

_LOGGER = logging.getLogger(__name__)

VALIDATE_STRUCTURE = "http://{}/"
ENDPOINT_STRUCTURE = "http://{}/api/v1/{}"
DEFAULT_TIMEOUT = 10


class DeliosClient:
    """Client for Delios Web Server."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize a new Client."""
        self._hass = hass
        self._host = host
        self._token = None

    async def validate(self) -> bool:
        """Validate the configured Host to check if it is a valid Delios Web Server."""
        try:
            endpoint = VALIDATE_STRUCTURE.format(self._host)
            session = aiohttp_client.async_get_clientsession(
                self._hass, verify_ssl=False
            )
            async with session.get(endpoint, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return True
        except asyncio.TimeoutError:
            return False
        except aiohttp.client_exceptions.ClientError:
            return False
        return False

    async def login(self, username: str, password: str) -> bool:
        """Login to Delios Web Server."""
        try:
            endpoint = ENDPOINT_STRUCTURE.format(self._host, "token")
            auth = aiohttp.BasicAuth(login=username, password=password)
            session = aiohttp_client.async_get_clientsession(
                self._hass, verify_ssl=False
            )
            async with session.get(
                endpoint, timeout=DEFAULT_TIMEOUT, auth=auth
            ) as response:
                if response.status == 200:
                    json = await response.json()
                    self._token = AccessToken(
                        api_key=json["api_key"],
                        expire=json["expire"],
                        level=json["level"],
                        username=json["username"],
                    )
                    return True
            return False
        except asyncio.TimeoutError:
            return False
        except aiohttp.client_exceptions.ClientError:
            return False
        return False

    async def sensors(self) -> SensorsData | None:
        """Request sensors data to Delios Web Server."""
        data = await self.__request("dashboard")
        if data is not None:
            return SensorsData(data)

    async def status(self) -> StatusData | None:
        """Request status data to Delios Web Server."""
        data = await self.__request("system/status")
        if data is not None:
            return StatusData(data)

    async def parameters(self) -> ParametersData | None:
        """Request parameters data to Delios Web Server."""
        data = await self.__request("info/system")
        if data is not None:
            return ParametersData(data)

    async def totalizer(self) -> TotalizerData | None:
        """Request totalizer data to Delios Web Server."""
        data = await self.__request("info/totalizer")
        if data is not None:
            return TotalizerData(data)

    async def firmware(self) -> FirmwareData | None:
        """Request firmware data to Delios Web Server."""
        data = await self.__request("info/firmware")
        if data is not None:
            return FirmwareData(data)

    async def __request(self, endpoint: str) -> dict | None:
        """Make a request to Delios Web Server."""
        if self._token is None:
            raise UnauthorizedClient
        session = aiohttp_client.async_get_clientsession(self._hass, verify_ssl=False)
        endpoint = ENDPOINT_STRUCTURE.format(self._host, endpoint)
        headers = {"x-access-token": self._token.api_key}
        async with session.get(
            endpoint, timeout=DEFAULT_TIMEOUT, headers=headers
        ) as response:
            if response.status == 401:
                raise UnauthorizedClient
            elif response.status == 200:
                return await response.json()


@dataclass
class AccessToken:
    """Access token representation for Delios Web Server."""

    api_key: str = ""
    expire: Optional[int] = None
    level: Optional[int] = None
    username: Optional[str] = None


class SensorsData:
    """Sensors data from Delios Web Server."""

    def __init__(self, data: dict) -> None:
        """Initialize sensors data from JSON."""
        self._data = {}
        if "variables" in data:
            for variable in data["variables"]:
                self._data[variable["ctrl_name"]] = variable["value"]

    def get(self, name: str) -> Any:
        """Read a single sensor value."""
        if name in self._data:
            return float(self._data[name])
        raise InvalidAttribute(name)


class StatusData:
    """Status data from Delios Web Server."""

    def __init__(self, data: dict) -> None:
        """Initialize status data from JSON."""
        self.usb = data["usb"]
        self.wifi = int(data["wifi"]) == 1
        self.lan = int(data["lan"]) == 1


class ParametersData:
    """Parameters data from Delios Web Server."""

    def __init__(self, data: dict) -> None:
        """Initialize paramters data from JSON."""
        self._data = {}
        if "variables" in data:
            for variable in data["variables"]:
                self._data[variable["ctrl_name"]] = variable["value"]

    def get(self, name: str) -> Any:
        """Read a single parameter value."""
        if name in self._data:
            return float(self._data[name])
        raise InvalidAttribute(name)


class TotalizerData:
    """Totalizer data from Delios Web Server."""

    def __init__(self, data: dict) -> None:
        """Initialize totalizer data from JSON."""
        self.photovoltaic = float(data["totalizers"]["TotalEnergyPV"])
        self.buyed = float(data["totalizers"]["TotalEnergyBuyed"])
        self.injected = float(data["totalizers"]["TotalEnergyInjected"])
        self.self_consumed = float(data["totalizers"]["TotalEnergySelfConsumed"])


class FirmwareData:
    """Firmware data from Delios Web Server."""

    def __init__(self, data: dict) -> None:
        """Initialize firmware data from JSON."""
        if "variables" in data:
            for variable in data["variables"]:
                if variable["ctrl_name"] == "MachineFW":
                    self.machine = int(variable["value"])
                elif variable["ctrl_name"] == "INVacFW":
                    self.grid = int(variable["value"])
                elif variable["ctrl_name"] == "INVpvFW":
                    self.photovoltaic = int(variable["value"])
                elif variable["ctrl_name"] == "INVbattFW":
                    self.battery = int(variable["value"])
                elif variable["ctrl_name"] == "firmware":
                    self.firmware = variable["value"]


class UnauthorizedClient(Exception):
    """Unauthorized client exception."""


class InvalidAttribute(Exception):
    """Invalid attribute exception."""

    def __init__(self, name: str) -> None:
        """Initialize an InvalidAttribute exception."""
        self.name = name
        self.message = f"Invalid attribute ({name})"
        super().__init__(self.message)
