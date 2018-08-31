
from tensorhive.config import SSH_CONFIG
from pssh.clients.native import ParallelSSHClient
from typing import Dict
# Useful doc: https://media.readthedocs.org/pdf/fabric-docs/stable/fabric-docs.pdf


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
