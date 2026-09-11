#!/usr/bin/env python3
"""Exercise the built image using disposable host data, never the live instance."""
import hashlib
import json
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'container'))
from nymea_rpc import insecure_tls_context, read_reply  # noqa: E402

IMAGE = 'nymea-local:trixie'
RUNTIME = '/usr/local/lib/nymea-container/'
COMPOSE_FILE = Path(__file__).resolve().parent.parent / 'docker-compose.yml'


def docker(*args, check=True):
    result = subprocess.run(['docker', *args], capture_output=True, text=True, check=False)
    if check and result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


class Client:
    def __init__(self, port):
        context = insecure_tls_context()
        self.sock = context.wrap_socket(socket.create_connection(('127.0.0.1', port), timeout=10))
        self.certificate = hashlib.sha256(self.sock.getpeercert(binary_form=True)).hexdigest()
        self.stream = self.sock.makefile('rb')
        self.sequence = 0
        self.token = None
        self.hello = self.call('JSONRPC.Hello')

    def call(self, method, **params):
        self.sequence += 1
        request = dict(id=self.sequence, method=method, params=params)
        if self.token:
            request['token'] = self.token
        self.sock.sendall(json.dumps(request).encode() + b'\n')
        while True:
            reply = read_reply(self.stream, self.sequence)
            if reply is None:
                continue
            assert reply.get('status') == 'success', reply
            return reply['params']

    def login(self, password):
        result = self.call('JSONRPC.Authenticate', username='smoke-test', password=password, deviceName='smoke-test')
        assert result['success'], result
        self.token = result['token']
        assert self.call('JSONRPC.Hello')['authenticated']

    def close(self):
        self.stream.close()
        self.sock.close()


def wait_healthy(name, previous_restart=None):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        info = json.loads(docker('inspect', name))[0]
        if previous_restart is None or info['RestartCount'] > previous_restart:
            if info['State'].get('Health', {}).get('Status') == 'healthy':
                return
        time.sleep(1)
    raise RuntimeError('Container did not become healthy: ' + docker('logs', '--tail', '50', name))


def compose_service():
    """Resolve docker-compose.yml so the smoke test can't drift from what Compose actually runs."""
    output = subprocess.run(['docker', 'compose', '-f', str(COMPOSE_FILE), 'config', '--format', 'json'],
                             capture_output=True, text=True, check=True)
    return json.loads(output.stdout)['services']['nymead']


def run(name, data):
    service = compose_service()
    args = ['run', '-d', '--name', name,
            '--network', service['network_mode'], '--uts', service['uts'],
            '--restart', service['restart'], '--health-interval', '2s']
    for tmpfs in service['tmpfs']:
        args += ['--tmpfs', tmpfs]
    for volume in service['volumes']:
        subdir = 'nymea' if volume['target'] == '/var/lib/nymea' else 'cache'
        args += ['-v', f"{data}/{subdir}:{volume['target']}"]
    args.append(IMAGE)
    docker(*args)
    wait_healthy(name)


def stop(name):
    docker('stop', '--time', '45', name)
    info = json.loads(docker('inspect', name))[0]
    assert info['State']['ExitCode'] == 0, info['State']
    docker('rm', name)


def main():
    name = 'nymea-smoke-' + uuid.uuid4().hex[:10]
    data = Path(tempfile.mkdtemp(prefix='nymea-smoke-'))
    restored = Path(tempfile.mkdtemp(prefix='nymea-restore-'))
    (data / 'nymea').mkdir()
    (data / 'cache').mkdir()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    (data / 'nymea' / 'nymead.conf').write_text(
        f'[TcpServer]\ndefault\\address=127.0.0.1\ndefault\\port={port}\n'
        'default\\sslEnabled=true\ndefault\\authenticationEnabled=true\n\n'
        '[WebServer]\ndisabled=true\n[WebSocketServer]\ndisabled=true\n[MqttServer]\ndisabled=true\n')
    password = secrets.token_urlsafe(24)
    print(f'Test data: {data}; restore target: {restored}', flush=True)
    try:
        run(name, data)
        client = Client(port)
        assert client.hello['initialSetupRequired']
        identity, certificate = client.hello['uuid'], client.certificate
        assert client.call('JSONRPC.CreateUser', username='smoke-test', password=password)['error'] == 'UserErrorNoError'
        client.login(password)
        classes = client.call('Integrations.GetThingClasses')['thingClasses']
        # Generic software devices need no external service or hardware.
        candidates = [c for c in classes if c.get('name') == 'genericthing']
        if not candidates:
            candidates = [c for c in classes if 'generic' in c.get('name', '').lower() and not c.get('paramTypes')]
        assert candidates, 'No parameter-free generic software thing class found'
        added = client.call('Integrations.AddThing', thingClassId=candidates[0]['id'], name='Persistence smoke test', thingParams=[])
        assert added['thingError'] == 'ThingErrorNoError', added
        thing_id = added['thingId']
        client.close()
        stop(name)
        run(name, data)
        client = Client(port)
        assert client.hello['uuid'] == identity and client.certificate == certificate
        assert not client.hello['initialSetupRequired']
        client.login(password)
        assert any(t['id'] == thing_id for t in client.call('Integrations.GetThings')['things'])
        client.close()
        print('PASS: API user, thing, UUID and certificate survive recreation', flush=True)
        stop(name)
        docker('run', '--rm', '--entrypoint', 'tar', '-v', f'{data}:/backup', IMAGE,
               '-C', '/backup', '-cf', '/backup/snapshot.tar', 'nymea', 'cache')
        docker('run', '--rm', '--entrypoint', 'tar', '-v', f'{data}:/backup:ro',
               '-v', f'{restored}:/restore', IMAGE, '-C', '/restore', '-xf', '/backup/snapshot.tar')
        run(name, restored)
        client = Client(port)
        assert client.hello['uuid'] == identity and client.certificate == certificate
        client.login(password)
        assert any(t['id'] == thing_id for t in client.call('Integrations.GetThings')['things'])
        client.close()
        print('PASS: stopped backup restores user, thing and identity into another folder', flush=True)
        docker('exec', name, 'supervisorctl', '-c', RUNTIME + 'supervisord.conf', 'signal', 'STOP', 'nymea')
        try:
            result = subprocess.run(['docker', 'exec', name, RUNTIME + 'healthcheck.py'], capture_output=True, timeout=15)
            assert result.returncode != 0, 'Health check accepted an unresponsive API'
        finally:
            docker('exec', name, 'supervisorctl', '-c', RUNTIME + 'supervisord.conf', 'signal', 'CONT', 'nymea')
        wait_healthy(name)
        print('PASS: health check rejects an unresponsive API', flush=True)
        for service in ('nymea', 'avahi', 'dbus'):
            info = json.loads(docker('inspect', name))[0]
            docker('exec', name, 'supervisorctl', '-c', RUNTIME + 'supervisord.conf', 'signal', 'KILL', service)
            wait_healthy(name, info['RestartCount'])
            print(f'PASS: {service} failure restarts the container and returns to healthy', flush=True)
        stop(name)
        print('PASS: graceful shutdown', flush=True)
    finally:
        if docker('container', 'inspect', name, check=False):
            docker('stop', '--time', '45', name, check=False)
            docker('rm', name, check=False)
        # Retain test artifacts for inspection; never delete an arbitrary bind mount.


if __name__ == '__main__':
    main()
