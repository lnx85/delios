# Home Assistant Delios component

[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=lnx85_delios&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=lnx85_delios) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=lnx85_delios&metric=security_rating)](https://sonarcloud.io/dashboard?id=lnx85_delios) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=lnx85_delios&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=lnx85_delios) [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=lnx85_delios&metric=ncloc)](https://sonarcloud.io/dashboard?id=lnx85_delios) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=lnx85_delios&metric=coverage)](https://sonarcloud.io/dashboard?id=lnx85_delios)

Please report any [issues](https://github.com/lnx85/delios/issues) and feel free to raise [pull requests](https://github.com/lnx85/delios/pulls).

[![BuyMeCoffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/lnx85)

This is a Home Assistant integration to support Delios inverters.

Using this integration does not stop your devices from sending status
to the Delios cloud, so this should not be seen as a security measure,
rather it improves speed and reliability by using local connections.

---

## Device support

Note that devices sometimes get firmware upgrades, so it is possible
that the device will not work despite being listed.

Currently supported devices are:

- IBRIDO DLS
- IBRIDO DLS-C

---

## Installation

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)

Installation is easiest via the [Home Assistant Community Store
(HACS)](https://hacs.xyz/), which is the best place to get third-party
integrations for Home Assistant. Once you have HACS set up, simply click the button below (requires My Homeassistant configured) or
follow the [instructions for adding a custom
repository](https://hacs.xyz/docs/faq/custom_repositories) and then
the integration will be available to install like any other.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=lnx85&repository=delios&category=integration)

## Configuration

After installing, you can easily configure your devices using the Integrations configuration UI. Go to Settings / Devices & Services and press the Add Integration button, or click the shortcut button below (requires My Homeassistant configured).

[![Add Integration to your Home Assistant
instance.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=delios)

### Stage One

The first stage of configuration is to provide the information needed to
connect to the inverter.

You will need to provide a name, your device's IP address or hostname,
device model, username and password; both default user and password
for Delios inverters are "user".

#### name

&nbsp;&nbsp;&nbsp;&nbsp;_(string) (Required)_ Any unique name for the
device. This will be used as the base for the entity names in Home
Assistant. Although Home Assistant allows you to change the name
later, it will only change the name used in the UI, not the name of
the entities.

#### host

&nbsp;&nbsp;&nbsp;&nbsp;_(string) (Required)_ IP or hostname of the device.

#### model

&nbsp;&nbsp;&nbsp;&nbsp;_(string) (Required)_ Device model.

#### username

&nbsp;&nbsp;&nbsp;&nbsp;_(string) (Required)_ Device username (default: user).

#### password

&nbsp;&nbsp;&nbsp;&nbsp;_(string) (Required)_ Device password (default: user).

#### scan interval

&nbsp;&nbsp;&nbsp;&nbsp;_(int) (Optional)_ Interval (in seconds) between two
updates.

At the end of this step, an attempt is made to connect to the device and see if
it returns any data. When succesfully connected, the device will show up in your
Home Assistant installation.

## Next steps

1. This component is mostly unit-tested thanks to the upstream project, but there are a few more to complete.
2. Once unit tests are complete, the next task is to complete the Home Assistant quality checklist before considering submission to the HA team for inclusion in standard installations.
