# nymea-docker

Run nymea on a native Linux Docker host, with settings and application data stored in one host folder. The image uses `debian:trixie-slim` and the stable nymea Trixie repository, published on Docker Hub as [`nymea/nymea`](https://hub.docker.com/r/nymea/nymea).

## Quick start

Install Docker Engine and the Docker Compose plugin using the [Docker installation instructions](https://docs.docker.com/engine/install/). This setup requires native Linux Docker Engine with host networking; Docker Desktop and rootless Docker are not supported targets.

```sh
cp .env.example .env
# Optionally edit NYMEA_DATA_DIR and TZ in .env.
docker compose up -d --build --wait --wait-timeout 120
```

Continue with [Usage](docs/usage/README.md) to connect nymea:app and create your first user.

## Documentation

| Topic | Description |
| --- | --- |
| [Usage](docs/usage/README.md) | Connecting nymea:app, day-to-day container commands |
| [Configuration](docs/configuration/README.md) | Host settings, data layout, `.env` variables |
| [Networking](docs/networking/README.md) | Ports, LAN discovery, host-networking port mapping |
| [Zigbee, Z-Wave and Modbus RTU](docs/hardware/README.md) | Passing through USB serial sticks and configuring nymea to use them |
| [Plugins and updates](docs/plugins/README.md) | Managing `packages.txt`, upgrading the image |
| [Backup and restore](docs/backup/README.md) | Backing up and restoring host data |
| [Health and validation](docs/health/README.md) | Health check behavior, running the smoke test |
| [Building and publishing](docs/building/README.md) | Building the image and publishing it to Docker Hub |
