# Plugins and updates

`packages.txt` contains the explicit integration package list. Edit it to add or remove packages available in the stable Trixie repository, then rebuild. The list retains available LAN/software integrations from the old setup, excluding hardware-only integrations and packages absent from Trixie.

The Daikin Python integration is excluded because the packaged Qt 6 daemon does not include Python plugin support. Some integrations, such as Nuki, provide both LAN and Bluetooth features; only their LAN features are usable here.

Zigbee, Z-Wave and Modbus RTU plugins additionally need their USB stick passed through in `docker-compose.yml` before they're usable — see [Zigbee, Z-Wave and Modbus RTU](../hardware/README.md) instead of just adding the package.

```sh
# Fetch the current base image and current stable repository packages.
docker compose build --pull --no-cache
# Recreate the container with the new image, retaining host data.
docker compose up -d --wait --wait-timeout 120
```

Packages update only when the image is rebuilt. Record the image ID before an upgrade and keep a stopped-instance data backup if rollback is needed (see [Backup and restore](../backup/README.md)); an older daemon may not understand data modified by a newer version. Installed package versions are recorded inside the image at `/usr/share/nymea-container/installed-packages.txt`.

To publish a rebuilt image to Docker Hub instead of just using it locally, see [Building and publishing](../building/README.md).
