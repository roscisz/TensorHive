
from tensorhive.config import SSH_CONFIG
from pssh.clients.native import ParallelSSHClient
from typing import Dict
import logging
log = logging.getLogger(__name__)


class SSHConnectionManager():
    '''Responsible for configuring, establishing and holding shell sessions'''
    connection_group = None
    connection_container = {}

    def __init__(self, config: Dict):
        hostnames = config.keys()
        self._connection_group = ParallelSSHClient(
            hosts=hostnames,
            host_config=config,
            timeout=SSH_CONFIG.CONNECTION_TIMEOUT,
            num_retries=SSH_CONFIG.CONNECTION_NUM_RETRIES
        )

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
        host_config = {hostname: SSH_CONFIG.AVAILABLE_NODES[hostname]}

        if self.connection_container.get(hostname) is None:
            # Create and store in cache
            self.connection_container[hostname] = ParallelSSHClient(
                hosts=host_config.keys(), host_config=host_config)

        # Return cached object
        return self.connection_container[hostname]

    @property
    def connections(self):
        return self._connection_group

    @staticmethod
    def test_all_connections(config):
        '''
        It checks if all of the defined hosts are accessible via SSH.
        Typically runs on each TensorHive startup.
        You can turn it off (TEST_CONNECTIONS_ON_STARTUP = False in ssh_config.py).
        '''
        log.info('Testing SSH configuration...')
        if not config:
            log.warning('Empty ssh configuration. Please check {}'.format(SSH_CONFIG.CONFIG_PATH))

        # 1. Establish connection
        hostnames = config.keys()
        connections = ParallelSSHClient(
            hosts=hostnames,
            host_config=config
            # Ignore custom timeout and number of retries in favour of default values
        )

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
