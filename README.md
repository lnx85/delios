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

## Energy dashboard

The integration exposes dedicated battery charge/discharge sensors so the battery
can be tracked in the Home Assistant Energy dashboard:

- **Battery Charge Power** / **Battery Discharge Power** _(kW)_: the instantaneous
  power flowing into and out of the battery, split by direction.
- **Battery Charge Energy Total** / **Battery Discharge Energy Total** _(kWh)_:
  cumulative energy stored into and drawn from the battery. The Delios API only
  reports instantaneous battery power, so these totals are computed by integrating
  the power over time and are restored across restarts.

To configure the battery in the Energy dashboard, go to Settings / Dashboards /
Energy, add a battery system, and select _Battery Charge Energy Total_ as the
energy going into the battery and _Battery Discharge Energy Total_ as the energy
coming out of the battery.

### Energy totals (photovoltaic / grid / self-consumption)

The **Photovoltaic / Buyed / Injected / Self Consumed Energy Total** sensors
_(kWh, `total_increasing`)_ are computed by **integrating the instantaneous power
over time** (trapezoidal rule, restored across restarts) — the same technique used
for the battery energy totals.

> **Why not the inverter's own totals?** The Delios `/info/totalizer` endpoint only
> commits its cumulative counters **once per day, at the inverter's local
> midnight**, and the inverter clock stays on standard time (it does not follow
> DST). Fed into the Energy dashboard, a whole day's energy therefore appeared in a
> single **01:00 bucket** (00:00 in winter) and was attributed to the wrong day.
> Integrating the live power instead produces correctly time-bucketed, DST-correct
> energy. These integrated sensors replace the former totalizer-based ones (same
> entity ids) and start accumulating from 0 on upgrade.

Use _Photovoltaic Energy Total_ as solar production, _Buyed Energy Total_ as grid
consumption and _Injected Energy Total_ as return to grid in the Energy dashboard.

### Instantaneous power flows

The integration also exposes the matching **instantaneous power** _(kW)_ so each
flow can be tracked live on a normal dashboard (power-flow cards, gauges, history):

- **Photovoltaic Power** — instantaneous PV production (`photovoltaic_power`).
- **Buyed Power** / **Injected Power** — power drawn from / fed into the grid,
  split by direction from the single signed grid power reported by the inverter.
- **Self Consumed Power** — the share of PV production consumed on site rather
  than exported.

> Sign convention (verified on an IBRIDO DLS unit): `PowerGrid > 0` is power
> drawn from the grid (buyed), `PowerGrid < 0` is power injected into the grid.
> If the readings are swapped on your inverter, flip the sign in
> `custom_components/delios/entity.py`.

## Next steps

1. This component is mostly unit-tested thanks to the upstream project, but there are a few more to complete.
2. Once unit tests are complete, the next task is to complete the Home Assistant quality checklist before considering submission to the HA team for inclusion in standard installations.
