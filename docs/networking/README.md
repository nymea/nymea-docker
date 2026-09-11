# Networking and discovery

## Port mapping

`docker-compose.yml` sets `network_mode: host`, not Docker's default bridge network. The container shares the host's network namespace outright: there is no NAT, no `-p`/`ports:` mapping, and no port translation of any kind. Whatever port nymead listens on inside the container is the exact same port other devices reach on the host's own LAN IP — nothing to publish, forward or keep in sync between "container port" and "host port," because there is only one port.

Practical consequences of that:

- `docker compose ps` and `docker ps` never show a `PORTS` column for this container — that's expected for host networking, not a misconfiguration. To see what's actually listening, check `nymead.conf` (or `docker exec <container> ss -tulpn`).
- Changing a listener's port in nymea:app or `data/nymea/nymead.conf` changes the port reachable on the host directly. There is no separate Compose-level port to update to match.
- A port already bound by another process on the host (another nymea instance, a different service) collides directly — the container fails to bind it with an `Address already in use` error, rather than being isolated by Docker's networking layer the way a bridge-network container would be. This is also why only one instance should run per host with the default ports.
- Firewall rules must be applied on the host itself (e.g. `ufw`, `nftables`); Docker's own port-publishing rules never come into play here since nothing is published.

## Ports

Allow the following ports from your LAN as needed, and check for other services already using them first:

| Port | Default use |
| --- | --- |
| TCP 2222 | Authenticated TLS nymea API; used by nymea:app and the health check |
| TCP 4444 | Authenticated secure WebSocket API |
| TCP 80 / 443 | nymea HTTP / HTTPS listeners |
| TCP 1883 | Authenticated MQTT broker |
| UDP 5353 | Avahi mDNS discovery |

These are nymead's defaults, configurable per-listener through nymea:app or directly in `nymead.conf`; whatever you set there is what ends up open on the host, per the port-mapping behavior above. Integration plugins may use additional multicast, broadcast or device-specific ports. LAN firewalls, Wi-Fi client isolation and VLAN boundaries can still prevent discovery even though the ports themselves are open. There is no multicast reflector in this image.

## Frontend and hardware access

The image does not include a separate web frontend. Use nymea:app to configure it. By default it does not expose USB devices or Bluetooth, and does not use privileged mode or mount the host's D-Bus socket. Zigbee, Z-Wave and Modbus RTU USB sticks can be passed through explicitly — see [Zigbee, Z-Wave and Modbus RTU](../hardware/README.md).

`nymead`'s packaged binary requests the `NET_ADMIN` file capability, which falls outside Docker's default capability bounding set and would otherwise make the binary fail to exec; the build drops that capability instead. Any plugin feature that genuinely needs `NET_ADMIN` (for example, low-level interface/route configuration) will not work in this container. If you hit that, add `cap_add: [NET_ADMIN]` to the Compose service instead of rebuilding with the capability restored on the binary.

## Coexisting with other mDNS responders

If another mDNS responder runs on the host, it must permit sharing UDP 5353. Avahi in this container permits coexistence. Check the logs for socket conflicts if discovery fails.
