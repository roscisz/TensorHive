
from tensorhive.config import SSH_CONFIG
from pssh.clients.native import ParallelSSHClient
# Useful doc: https://media.readthedocs.org/pdf/fabric-docs/stable/fabric-docs.pdf


class SSHConnectionManager():
    '''Responsible for configuring, establishing, holding shell sessions'''

    def __init__(self, nodes):
        hosts = nodes.keys()
        self._connection_group = ParallelSSHClient(hosts, host_config=nodes)
        

    def add_connection(self, node):
        pass

    @property
    def connections(self):
        return self._connection_group