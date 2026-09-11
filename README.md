# nymea-docker

Run nymea on a native Linux Docker host, with settings and application data stored in one host folder. The image uses `debian:trixie-slim` and the stable nymea Trixie repository.

## Start

Install Docker Engine and the Docker Compose plugin using the [Docker installation instructions](https://docs.docker.com/engine/install/). This setup requires native Linux Docker Engine with host networking; Docker Desktop and rootless Docker are not supported targets.

```sh
cp .env.example .env
# Optionally edit NYMEA_DATA_DIR and TZ in .env.
docker compose up -d --build --wait --wait-timeout 120
```

Open nymea:app on the same LAN. Select the discovered instance and create your first user. If discovery is blocked by your network, add the Docker host's LAN IP manually using the TLS TCP API on port **2222**.

Only run one instance on a host with the default ports. Host networking shares the host's interfaces directly, enabling multicast and LAN discovery without port forwarding. Host UTS shares the host's hostname so Avahi advertises that hostname and its actual LAN addresses. The container runs its own D-Bus and Avahi; host D-Bus, systemd and Avahi are not required.

```sh
docker compose ps
docker compose logs -f --tail 100 nymead
docker compose stop
docker compose start
# Remove the container; host data stays in place.
docker compose down
```

## Host settings and data

| Setting | Default | Purpose |
| --- | --- | --- |
| `NYMEA_DATA_DIR` | `./data` | Host folder; relative paths resolve from the Compose project directory. |
| `TZ` | `Europe/Vienna` | Container timezone, for example `Etc/UTC`. |

```text
data/
  nymea/     # /var/lib/nymea: settings, users, certificates, scripts, databases
  cache/     # /var/cache/nymea: cached application state
```

Settings are managed through nymea:app. Advanced configuration is in `data/nymea/nymead.conf`; stop the container before editing it and start it afterwards. nymea 1.15 and newer store configuration under `/var/lib/nymea`, not `/etc/nymea`.

The daemon runs as root inside the container and creates root-owned files in the bind mounts. Use `sudo` when editing or backing up these files; do not make the directory world-writable. Container recreation and image rebuilds retain the host data. Transient D-Bus, Avahi and Supervisor files live in a temporary `/run` filesystem.

Existing `configs/` folders from the previous setup are left untouched and are not loaded. This is a fresh deployment: no settings or InfluxDB history are migrated. InfluxDB is not included; historical charts that need it are unavailable.

The packaged daemon still attempts to connect to InfluxDB and emits `LogEngine` connection warnings when it is absent. These do not prevent device control or API access. Warnings about unavailable system/update plugins, NetworkManager and Bluetooth are also expected in this LAN-only container; manage the host network and image updates on the host.

The default data folders and `.env` are Git-ignored. Put custom data folders outside the checkout, or add their path to your local `.git/info/exclude`. The Docker build context uses an allowlist, so runtime files are excluded even when a custom data folder is inside the checkout.

## Networking and discovery

Allow the following ports from your LAN as needed, and check for other services already using them:

| Port | Default use |
| --- | --- |
| TCP 2222 | Authenticated TLS nymea API; used by nymea:app and the health check |
| TCP 4444 | Authenticated secure WebSocket API |
| TCP 80 / 443 | nymea HTTP / HTTPS listeners |
| TCP 1883 | Authenticated MQTT broker |
| UDP 5353 | Avahi mDNS discovery |

Integration plugins may use additional multicast, broadcast or device-specific ports. LAN firewalls, Wi-Fi client isolation and VLAN boundaries can still prevent discovery. There is no multicast reflector in this image. Host networking means Compose `ports:` mappings do not apply.

The image does not include a separate web frontend. Use nymea:app to configure it. It does not expose USB devices, Bluetooth or Zigbee/Z-Wave radios, and does not use privileged mode or mount the host's D-Bus socket.

If another mDNS responder runs on the host, it must permit sharing UDP 5353. Avahi in this container permits coexistence. Check the logs for socket conflicts if discovery fails.

## Plugins and updates

`packages.txt` contains the explicit integration package list. Edit it to add or remove packages available in the stable Trixie repository, then rebuild. The list retains available LAN/software integrations from the old setup, excluding hardware-only integrations and packages absent from Trixie.

The Daikin Python integration is excluded because the packaged Qt 6 daemon does not include Python plugin support. Some integrations, such as Nuki, provide both LAN and Bluetooth features; only their LAN features are usable here.

```sh
# Fetch the current base image and current stable repository packages.
docker compose build --pull --no-cache
# Recreate the container with the new image, retaining host data.
docker compose up -d --wait --wait-timeout 120
```

Packages update only when the image is rebuilt. Record the image ID before an upgrade and keep a stopped-instance data backup if rollback is needed; an older daemon may not understand data modified by a newer version. Installed package versions are recorded inside the image at `/usr/share/nymea-container/installed-packages.txt`.

## Backup and restore

Stop nymea before copying the entire data folder so databases and configuration are consistent. Substitute your configured host path and a new backup filename:

```sh
docker compose stop
sudo tar -C ./data -czf nymea-backup.tar.gz nymea cache
docker compose start
```

Restore into an **empty** folder, preserving ownership:

```sh
docker compose stop
sudo mkdir -p /srv/nymea-restored
sudo tar -C /srv/nymea-restored -xzf nymea-backup.tar.gz
# Set NYMEA_DATA_DIR=/srv/nymea-restored in .env.
docker compose up -d --force-recreate --wait --wait-timeout 120
```

Keep backups outside the checkout; they include user credentials and private certificates.

## Health and validation

Supervisor orders D-Bus, Avahi and nymea startup and shuts everything down if a required service exits. Docker restarts the container unless you explicitly stopped it. Logs rotate at 10 MB with three files retained.

The health check verifies all supervised processes and performs a TCP API handshake against the persisted instance UUID. It reads the configured TCP address, port and TLS setting, so changing the port does not require editing the image. Keep at least one TCP API enabled. Docker marks an unresponsive API unhealthy; it does not restart containers solely because a health check fails.

```sh
docker compose config --quiet
# After building: isolated lifecycle/persistence tests using temporary data.
python3 tests/smoke.py
```

The smoke test requires Docker access and uses a temporary TCP port with the web, WebSocket and MQTT listeners disabled. It creates a disposable user and software thing, tests recreation, backup/restore and required-service failure recovery, and removes its containers afterwards. It never uses your configured data folder.

To finish LAN acceptance testing, connect nymea:app from a second device, confirm automatic discovery, and discover a real LAN device using its integration plugin.
