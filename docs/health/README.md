# Health and validation

Supervisor orders D-Bus, Avahi and nymea startup and shuts everything down if a required service exits. Docker restarts the container unless you explicitly stopped it. Logs rotate at 10 MB with three files retained.

The health check verifies all supervised processes and performs a TCP API handshake against the persisted instance UUID. It reads the configured TCP address, port and TLS setting, so changing the port does not require editing the image. Keep at least one TCP API enabled. Docker marks an unresponsive API unhealthy; it does not restart containers solely because a health check fails.

## Smoke test

```sh
docker compose config --quiet
# After building: isolated lifecycle/persistence tests using temporary data.
python3 tests/smoke.py
```

The smoke test requires Docker access and uses a temporary TCP port with the web, WebSocket and MQTT listeners disabled. It creates a disposable user and software thing, tests recreation, backup/restore and required-service failure recovery, and removes its containers afterwards. It never uses your configured data folder.

Run this before [publishing a new image](../building/README.md#before-publishing).

## LAN acceptance testing

To finish LAN acceptance testing, connect nymea:app from a second device, confirm automatic discovery, and discover a real LAN device using its integration plugin.
