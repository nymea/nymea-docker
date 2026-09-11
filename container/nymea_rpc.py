"""Shared TLS/JSON-RPC helpers for nymea's TCP API, used by the health check and smoke test."""
import json
import ssl


def insecure_tls_context():
    """For a local readiness/test check only: nymea's certificate is self-signed, not CA-issued."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def read_reply(stream, expected_id, limit=65536):
    """Read one JSON-RPC line; return it if its id matches, else None."""
    reply = json.loads(stream.readline(limit))
    if not isinstance(reply, dict) or reply.get("id") != expected_id:
        return None
    return reply
