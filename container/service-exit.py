#!/usr/bin/python3
"""Stop the whole container if a required service exits, including exit code 0."""
import os
import signal
import sys

from supervisor import childutils

while True:
    headers, payload = childutils.listener.wait()
    fields = dict(field.split(":", 1) for field in payload.split())
    childutils.listener.ok()
    if fields.get("processname") in {"dbus", "avahi", "nymea"}:
        print(f"Required service {fields['processname']} failed; stopping container", file=sys.stderr, flush=True)
        os.kill(os.getppid(), signal.SIGTERM)
