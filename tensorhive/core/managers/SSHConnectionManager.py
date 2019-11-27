from tensorhive.config import SSH
from pssh.clients.native import ParallelSSHClient
from pssh.exceptions import PKeyFileError
from paramiko.rsakey import RSAKey
from typing import Dict
from tensorhive.core import ssh
import logging
log = logging.getLogger(__name__)


class SSHConnectionManager():
    '''Responsible for configuring, establishing and holding shell sessions'''
    _connection_group = None
    _connection_container = {}  # type: Dict

    def __init__(self, config: Dict, ssh_key_path: str):
        self.ssh_key_path = ssh_key_path
        self._connection_group = self.new_parallel_ssh_client(config, key_path=ssh_key_path)

    @classmethod
    def new_parallel_ssh_client(cls, config, key_path=None) -> ParallelSSHClient:
        hostnames = config.keys()
        try:
            if SSH.PROXY:
                client = ParallelSSHClient(
                    hosts=hostnames,
                    host_config=config,
                    pkey=key_path,
                    proxy_host=SSH.PROXY['proxy_host'],
                    proxy_user=SSH.PROXY['proxy_user'],
                    proxy_port=SSH.PROXY['proxy_port']
                    # Ignore timeout and num_retires for proxy
                )
            else:
                client = ParallelSSHClient(
                    hosts=hostnames,
                    host_config=config,
                    timeout=SSH.TIMEOUT,
                    pkey=key_path,
                    num_retries=SSH.NUM_RETRIES
                )
        except PKeyFileError as e:
            log.error('[✘] {}'.format(str(e)))
            return None
        else:
            return client

    def add_host(self, host_config: Dict):
        '''
        Appends a host (as hostname + config) directly into parallel ssh client instance.

        Expected dict structure:
        host_config = {'<some_hostname>': {'user': '<some_username>'}}
        '''
        hostname = [*host_config][0]
        self.connections.hosts = [*self.connections.hosts, hostname]
        self.connections.host_config = {
            **self.connections.host_config, **host_config
        }

    def single_connection(self, hostname: str):
        config = {hostname: SSH.AVAILABLE_NODES[hostname]}

        if not self._connection_container.get(hostname):
            # Create and store in cache
            self._connection_container[hostname] = self.new_parallel_ssh_client(config, self.ssh_key_path)

        # Return cached object
        return self._connection_container[hostname]

    @property
    def connections(self):
        return self._connection_group

    @staticmethod
    def test_all_connections(config, key_path=None):
        '''
        It checks if all of the defined hosts are accessible via SSH.
        Typically runs on each TensorHive startup.
        You can turn it off (INI config -> [ssh] -> test_on_startup = off
        '''
        key_descr = 'default system keys' if key_path is None else 'key: {}'.format(key_path)
        log.info('[⚙] Testing SSH connections using {}'.format(key_descr))

        # 1. Establish connection
        connections = SSHConnectionManager.new_parallel_ssh_client(config, key_path=key_path)
        if not connections:
            log.info('[✘] Could not establish connection.')
            return len(config)

        # 2. Execute and gather output
        command = 'uname'
        message_template = '[{icon}] {host:20} {msg}'
        output = connections.run_command(command, stop_on_errors=False)
        connections.join(output)

        # 3. Log appropriate messages based on command's result
        num_failed = 0
        for host, host_output in output.items():
            if host_output.exception is None and host_output.exit_code == 0:
                log.info(message_template.format(
                    icon='✔',
                    host=host,
                    msg='OK'))
            else:
                num_failed += 1
                error_message = 'FAILED (exit code: {}, exception: {})'.format(
                    host_output.exit_code,
                    host_output.exception.__class__.__name__)
                log.critical(message_template.format(
                    icon='✘',
                    host=host,
                    msg=error_message))

        # 4. Show simple summary of failed connections
        if num_failed > 0:
            log.info('Summary: {failed}/{all} failed to connect.'.format(
                failed=num_failed,
                all=len(output)))

        return num_failed
