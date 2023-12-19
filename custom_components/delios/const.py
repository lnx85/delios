"""Module constants."""

DOMAIN = "delios"

MODELS: list[str] = [
    "IBRIDO DLS",
    "IBRIDO DLS-C",
]

CONF_NAME = "name"
CONF_MODEL = "model"
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_USERNAME = "user"
DEFAULT_SCAN_INTERVAL = 10

SYSTEM_UPDATE_INTERVAL = 60 * 60 * 24
