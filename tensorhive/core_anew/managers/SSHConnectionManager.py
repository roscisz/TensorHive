
import fabric
from tensorhive.config import SSH_CONFIG
# Useful doc: https://media.readthedocs.org/pdf/fabric-docs/stable/fabric-docs.pdf


class SSHConnectionManager():
    '''Responsible for configuring, establishing, holding shell sessions'''

    def __init__(self, nodes):
        setup_connection = lambda node: fabric.Connection(node, 
            connect_timeout=SSH_CONFIG.CONNECTION_TIMEOUT)
        connections = [setup_connection(node) for node in nodes]
        self._connection_group = fabric.ThreadingGroup.from_connections(
            connections)

    def add_connection(self, node):
        self._connection_group.extend(fabric.Connection(node))


    @property
    def connections(self):
        return self._connection_group