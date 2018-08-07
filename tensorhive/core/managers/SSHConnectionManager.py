
from tensorhive.config import SSH_CONFIG
from pssh.clients.native import ParallelSSHClient
from typing import Dict
# Useful doc: https://media.readthedocs.org/pdf/fabric-docs/stable/fabric-docs.pdf


class SSHConnectionManager():
    '''Responsible for configuring, establishing and holding shell sessions'''
    connection_group = None

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

    @staticmethod
    def establish_connection(host_config: Dict):
        return ParallelSSHClient(
                hosts=host_config.keys(),
                host_config=host_config,
                timeout=SSH_CONFIG.CONNECTION_TIMEOUT,
                num_retries=SSH_CONFIG.CONNECTION_NUM_RETRIES)

    @property
    def connections(self):
        return self._connection_group
