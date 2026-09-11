#!/usr/bin/python3
"""Wait for a private D-Bus service before replacing this process."""
import os
import re
import subprocess
import sys
import time

AVAHI_SERVER_RUNNING = 2

# Each entry: dbus-send target args, and a readiness check over the reply
# (None means "any successful reply is ready").
SERVICES = {
    "dbus": (
        ["--dest=org.freedesktop.DBus", "/", "org.freedesktop.DBus.GetId"],
        None,
    ),
    "avahi": (
        ["--dest=org.freedesktop.Avahi", "/", "org.freedesktop.Avahi.Server.GetState"],
        AVAHI_SERVER_RUNNING,
    ),
}

service, *command = sys.argv[1:]
try:
    target, expected_state = SERVICES[service]
except KeyError:
    sys.exit(f"Unknown service: {service}")


def ready(stdout):
    if expected_state is None:
        return True
    match = re.search(r"int32 (-?\d+)", stdout)
    return match is not None and int(match.group(1)) == expected_state


deadline = time.monotonic() + 20
while time.monotonic() < deadline:
    result = subprocess.run(
        ["dbus-send", "--system", "--print-reply", "--reply-timeout=1000", *target],
        capture_output=True, text=True, timeout=2,
    )
    if result.returncode == 0 and ready(result.stdout):
        os.execvp(command[0], command)
    time.sleep(0.2)
sys.exit(f"Timed out waiting for {service}")
