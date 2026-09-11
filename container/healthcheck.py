#!/usr/bin/python3
"""Check required processes and the persisted instance's TCP API handshake."""
import configparser
import json
import socket
import ssl
import sys

from supervisor import childutils


def check():
    rpc = childutils.getRPCInterface({"SUPERVISOR_SERVER_URL": "unix:///run/supervisor.sock"})
    processes = {p["name"]: p["statename"] for p in rpc.supervisor.getAllProcessInfo()}
    for name in ("dbus", "avahi", "nymea", "required-service-exit"):
        if processes.get(name) != "RUNNING":
            raise RuntimeError(f"{name} is not running")

    config = configparser.ConfigParser(interpolation=None)
    config.read("/var/lib/nymea/nymead.conf")
    section = config["TcpServer"]
    if section.getboolean("disabled", fallback=False):
        raise RuntimeError("Health check requires an enabled TCP API")
    # QSettings serializes nested groups as backslash-separated keys.
    endpoints = sorted(key[:-5] for key in section if key.endswith("\\port"))
    errors = []
    for endpoint in endpoints:
        try:
            address = section[endpoint + "\\address"]
            address = {"0.0.0.0": "127.0.0.1", "::": "::1"}.get(address, address)
            with socket.create_connection((address, section.getint(endpoint + "\\port")), timeout=2) as raw:
                connection = raw
                if section.getboolean(endpoint + "\\sslEnabled", fallback=True):
                    # Local readiness check: nymea generates a self-signed certificate.
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    connection = context.wrap_socket(raw, server_hostname=address)
                with connection:
                    connection.sendall(b'{"id":1,"method":"JSONRPC.Hello","params":{}}\n')
                    with connection.makefile("rb") as stream:
                        for _ in range(4):
                            reply = json.loads(stream.readline(65536))
                            if reply.get("id") != 1:
                                continue
                            params = reply.get("params", {})
                            expected_uuid = config.get("nymead", "uuid")
                            if params.get("uuid") != expected_uuid or not params.get("version"):
                                raise RuntimeError("API handshake did not match this instance")
                            return
                        raise RuntimeError("Missing API handshake response")
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            errors.append(str(error))
    raise RuntimeError("No healthy TCP API: " + "; ".join(errors))


if __name__ == "__main__":
    try:
        check()
    except Exception as error:
        print(error, file=sys.stderr)
        sys.exit(1)
