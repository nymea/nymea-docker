# Zigbee, Z-Wave and Modbus RTU (serial devices)

By default this container exposes no host hardware: `docker-compose.yml` sets no `devices:`, isn't `privileged`, and doesn't bind-mount `/dev` (see [Networking](../networking/README.md#frontend-and-hardware-access)). Any `/dev/ttyS*` nodes visible inside the container are the container's own dummy legacy UART devices, not a host USB stick — a real Zigbee/Z-Wave coordinator or Modbus RTU adapter needs to be passed through explicitly. This is opt-in and requires editing `docker-compose.yml`, `packages.txt` and rebuilding the image.

## 1. Find a stable device path on the host

USB-serial device names (`/dev/ttyUSB0`, `/dev/ttyACM0`, ...) are assigned in enumeration order and can shift across reboots or replugging, especially with more than one stick attached. Use the udev-managed stable path instead:

```sh
ls -l /dev/serial/by-id/
```

Each entry there is a symlink naming the device by vendor/product/serial number, always pointing at the same physical stick regardless of enumeration order. Use these paths (not the plain `/dev/ttyUSB*`/`ttyACM*` names) in the mapping below.

## 2. Pass the device through in `docker-compose.yml`

Add one `devices:` entry per stick, mapping the stable host path to a fixed, descriptive path inside the container:

```yaml
services:
  nymead:
    devices:
      - /dev/serial/by-id/usb-Nabu_Casa_ZBT-1_XXXXXXXX-if00-port0:/dev/ttyZigbee
      - /dev/serial/by-id/usb-0658_0200_XXXXXXXX-if00:/dev/ttyZwave
      - /dev/serial/by-id/usb-FTDI_USB-RS485_Cable_XXXXXXXX-if00-port0:/dev/ttyModbus
```

Substitute the actual paths from step 1 and drop any lines for hardware you don't have. This is the same minimal-privilege approach the rest of this setup uses: only the specific device nodes you list become accessible, nothing else in `/dev`. The alternative — bind-mounting all of `/dev` or running `privileged: true` — makes every host device (and, for `privileged`, effectively full host access) visible instead of just the sticks you intend to use, and isn't necessary for this to work; use it only if you need devices to attach without editing Compose per stick.

The container runs `nymead` as root, so no `dialout` group membership or extra capability is needed to open the mapped device node.

## 3. Add the required plugin packages

Add the packages for the hardware you're using to `packages.txt`:

| Hardware | Packages to add |
| --- | --- |
| Zigbee | `nymea-plugin-zigbee-generic` for spec-compliant devices, plus any vendor-specific plugin you need (`nymea-plugin-zigbee-tradfri`, `-lumi`, `-osram`, `-philipshue`, `-develco`, `-eurotronic`, `-gewiss`, `-jung`, `-schneiderelectric`, `-tuya`), or `nymea-plugins-zigbee` to install all of them at once. `libnymea-zigbee1` is pulled in automatically. |
| Z-Wave | `nymea-zwave-plugin-openzwave` (the OpenZWave backend, required) plus `nymea-plugin-zwave-generic` for spec-compliant devices and/or vendor plugins (`nymea-plugin-zwave-fibaro`, `-qubino`, `-springswindowfashions`), or `nymea-plugins-zwave` for all of them. |
| Modbus RTU | `nymea-plugin-modbuscommander` — already included in this image's default `packages.txt`; RTU vs. TCP is a configuration choice in step 4, not a different package. |

Then rebuild:

```sh
docker compose build
docker compose up -d --wait --wait-timeout 120
```

## 4. Configure the hardware resource in nymea:app

Each of these hardware types is backed by a "hardware resource" in nymead, separate from the plugins that expose actual things through it. In nymea:app, open the settings/hardware resources page for the relevant subsystem (Zigbee network, Z-Wave network, or Modbus RTU master) and point it at the container-side path you chose in step 2 (`/dev/ttyZigbee`, `/dev/ttyZwave`, `/dev/ttyModbus` in the example above), setting the baud rate and any other serial parameters your adapter's manual specifies. Once the resource is up, the corresponding plugin(s) installed in step 3 can discover and add things through it.

## Notes

- Adding a stick after the container is already running requires adding its `devices:` entry and recreating the container (`docker compose up -d`); hot-adding a device to an already-running container isn't supported by Docker.
- If a stick stops working after a host reboot, confirm its `/dev/serial/by-id/...` symlink didn't disappear (e.g. the stick moved to a USB hub that enumerates differently) rather than assuming the container is at fault.
- This changes the "no USB device passthrough" default described in [Networking](../networking/README.md#frontend-and-hardware-access) — that page describes the image's defaults, this page describes the opt-in path to enable specific hardware.
