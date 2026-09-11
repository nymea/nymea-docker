# InfluxDB support (optional)

nymea's `LogEngine` uses InfluxDB to store historical thing states — the history charts in nymea:app need it. It is not included by default: without it, `nymead` logs (harmless) `LogEngine` connection warnings and history charts stay empty, but device control and the API are unaffected.

This adds InfluxDB **1.8** (the version nymead's packaged `LogEngine` plugin speaks) as a second, host-networked service alongside `nymead`.

**Alternative:** if you don't want history charts and just want the `LogEngine` connection warnings gone, skip InfluxDB entirely and set `NYMEAD_EXTRA_ARGS=-m` in `.env` instead — this starts `nymead` with `--no-logengine`, disabling the log engine outright. See [Configuration](../configuration/README.md).

## 1. Add the service

Add an `influxdb` service to `docker-compose.yml`, next to `nymead`:

```yaml
services:
  nymead:
    # ... unchanged ...

  influxdb:
    image: influxdb:1.8
    network_mode: host
    restart: unless-stopped
    environment:
      TZ: ${TZ:-Europe/Vienna}
      INFLUXDB_HTTP_BIND_ADDRESS: 127.0.0.1:8086
      INFLUXDB_DB: nymea
      INFLUXDB_ADMIN_USER: admin
      INFLUXDB_ADMIN_PASSWORD: ${INFLUXDB_ADMIN_PASSWORD:?set in .env}
      INFLUXDB_USER: nymea
      INFLUXDB_USER_PASSWORD: ${INFLUXDB_USER_PASSWORD:?set in .env}
      INFLUXDB_HTTP_AUTH_ENABLED: "true"
      INFLUXDB_MONITOR_STORE_ENABLED: "false"
      INFLUXDB_HTTP_LOG_ENABLED: "false"
    volumes:
      - ${NYMEA_DATA_DIR:-./data}/influxdb:/var/lib/influxdb
```

`network_mode: host` matches `nymead` so the two can reach each other without a shared Docker network. `INFLUXDB_HTTP_BIND_ADDRESS` keeps InfluxDB's API on `127.0.0.1` only — it is not meant to be reachable from the LAN, unlike nymead's own listeners.

The `INFLUXDB_*` variables only take effect on the **first** start against an empty data folder (InfluxDB's own init behavior); changing them afterwards has no effect until the volume is wiped.

## 2. Set credentials and start it

Add to `.env`:

```sh
INFLUXDB_ADMIN_PASSWORD=<choose a strong password>
INFLUXDB_USER_PASSWORD=<choose a strong password>
```

```sh
docker compose up -d --wait --wait-timeout 120
```

## 3. Point nymead at it

Stop the container, edit `data/nymea/nymead.conf`, then start it again:

```sh
docker compose stop
```

```ini
[Logs]
logDBHost=127.0.0.1
logDBName=nymea
logDBUser=nymea
logDBPassword=<same value as INFLUXDB_USER_PASSWORD>
```

```sh
docker compose start
```

## 4. Verify

```sh
docker compose logs -f --tail 100 nymead
```

`LogEngine` connection warnings should stop appearing. History charts in nymea:app populate as new states are logged.

## Backup

Include `influxdb` in the data folder backup alongside `nymea`, `cache` and `backups` — see [Backup and restore](../backup/README.md).
