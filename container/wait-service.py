#!/usr/bin/python3
"""Wait for a private D-Bus service before replacing this process."""
import os
import subprocess
import sys
import time

service, *command = sys.argv[1:]
if service == "dbus":
    target = ["--dest=org.freedesktop.DBus", "/", "org.freedesktop.DBus.GetId"]
elif service == "avahi":
    target = ["--dest=org.freedesktop.Avahi", "/", "org.freedesktop.Avahi.Server.GetState"]
else:
    sys.exit(f"Unknown service: {service}")

deadline = time.monotonic() + 20
while time.monotonic() < deadline:
    result = subprocess.run(
        ["dbus-send", "--system", "--print-reply", "--reply-timeout=1000", *target],
        capture_output=True, text=True, timeout=2,
    )
    if result.returncode == 0 and (service == "dbus" or "int32 2" in result.stdout):
        os.execvp(command[0], command)
    time.sleep(0.2)
sys.exit(f"Timed out waiting for {service}")
