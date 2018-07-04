class ConnectionManager():
    '''
    Responsible for establishing, holding connections etc.

    In case of SSHConnector, connection should be opened and closed in place where it's been used:
    example: 
    ```
        <context of some Monitor>
        with connection in connection_manager.connections
            <conneciton is automatically established here...>
            connection.run(...)
        <connection is automatically released here...>
    ```
    '''
    # FIXME hardcoded for sshconnector from spur

    def __init__(self, injected_connector):
        self._connector = injected_connector
        self._connections = []

    def add_node(self, hostname, username):
        connection = self._connector.shell_connection(hostname, username)
        self._connections.append(connection)

    @property
    def connections(self):
        '''Returns all available connections'''
        return self._connections
