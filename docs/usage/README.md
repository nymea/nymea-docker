# Usage

## Connecting nymea:app

Open nymea:app on the same LAN as the Docker host. Select the discovered instance and create your first user. If discovery is blocked by your network, add the Docker host's LAN IP manually using the TLS TCP API on port **2222** — see [Networking](../networking/README.md) for the full port list and how host networking exposes them.

Only run one instance on a host with the default ports (see [Networking](../networking/README.md)). Host networking shares the host's interfaces directly, enabling multicast and LAN discovery without port forwarding. Host UTS shares the host's hostname so Avahi advertises that hostname and its actual LAN addresses. The container runs its own D-Bus and Avahi; host D-Bus, systemd and Avahi are not required.

## Day-to-day commands

```sh
docker compose ps
docker compose logs -f --tail 100 nymead
docker compose stop
docker compose start
# Remove the container; host data stays in place.
docker compose down
```

## Interactive CLI (nymea-cli)

The image includes [`nymea-cli`](https://github.com/nymea/nymea-cli), a keyboard-driven terminal UI for browsing things, states and actions and executing actions directly against the running instance — useful for quick checks without opening nymea:app. Run it inside the container:

```sh
docker compose exec nymead nymea-cli --ssl --host 127.0.0.1 --port 2222
```

On first connect it asks for a username and password (or pass them directly: `--username <user> --password <password>`) and prompts you to accept the instance's TLS certificate fingerprint. Both the auth token and the accepted fingerprint are then stored in `/var/lib/nymea/nymea-cli.conf` — inside the bind-mounted data folder — so you won't be asked again after the container is recreated.

Basic navigation: arrow keys move between the thing list and its overview/params/states/actions panels, `Enter` opens an action's execute dialog, `Space` inspects a param, state or action's metadata, and `q` or `Esc` quits. Run `docker compose exec nymead nymea-cli --help` for the full flag list.

## What's next

- [Configuration](../configuration/README.md) for host settings, data layout and advanced `nymead.conf` editing.
- [Backup and restore](../backup/README.md) before any upgrade.
- [Health and validation](../health/README.md) to understand health check behavior and run the smoke test.
