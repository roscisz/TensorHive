
from tensorhive.config import SSH
from pssh.clients.native import ParallelSSHClient
from typing import Dict
import logging
log = logging.getLogger(__name__)


class SSHConnectionManager():
    '''Responsible for configuring, establishing and holding shell sessions'''
    _connection_group = None
    _connection_container = {}

    def __init__(self, config: Dict):
        self._connection_group = self.new_parallel_ssh_client(config)

    @classmethod
    def new_parallel_ssh_client(cls, config) -> ParallelSSHClient:
        hostnames = config.keys()
        if SSH.PROXY:
            return ParallelSSHClient(
                hosts=hostnames,
                host_config=config,
                proxy_host=SSH.PROXY['proxy_host'],
                proxy_user=SSH.PROXY['proxy_user'],
                proxy_port=SSH.PROXY['proxy_port']
                # Ignore timeout and num_retires for proxy
            )

        return ParallelSSHClient(
            hosts=hostnames,
            host_config=config,
            timeout=SSH.TIMEOUT,
            num_retries=SSH.NUM_RETRIES)

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
            self._connection_container[hostname] = self.new_parallel_ssh_client(config)

        # Return cached object
        return self._connection_container[hostname]

    @property
    def connections(self):
        return self._connection_group

    @staticmethod
    def test_all_connections(config):
        '''
        It checks if all of the defined hosts are accessible via SSH.
        Typically runs on each TensorHive startup.
        You can turn it off (INI config -> [ssh] -> test_on_startup = off
        '''
        log.info('[⚙] Testing SSH configuration...')
        if not config:
            log.warning('[!] Empty ssh configuration. Please check {}'.format(SSH.HOSTS_CONFIG_FILE))

        # 1. Establish connection
        connections = SSHConnectionManager.new_parallel_ssh_client(config)

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
            log.critical('Summary: {failed}/{all} failed to connect.'.format(
                failed=num_failed,
                all=len(output)))
