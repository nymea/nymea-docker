# Configuration

## Host settings

| Setting | Default | Purpose |
| --- | --- | --- |
| `NYMEA_DATA_DIR` | `./data` | Host folder; relative paths resolve from the Compose project directory. |
| `TZ` | `Europe/Vienna` | Container timezone, for example `Etc/UTC`. |

Set these in `.env` (copy `.env.example` first — see the top-level [README](../../README.md)).

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
