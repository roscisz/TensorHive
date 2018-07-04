from tensorhive.core_anew.connectors.SSHConnector import SSHConnector
class ConnectionManager():
    '''
    Responsible for establishing, holding connections etc.

    In case of SSHConnector, is opened and closed by default in place, where it was used:
    example: 
    ```
        <context of some Monitor>
        with connection in connection_manager.connections
            <conneciton is automatically established here...>
            connection.run(...)
        <connection is automatically released here...>
    ```
    '''

    def __init__(self, injected_connector=None):
        self._connectors = []
        if injected_connector is not None:
            self.add_connector(injected_connector)

    def add_connector(self, connector):
        self._connectors.append(connector)

    @property
    def connections(self):
        '''Returns new connections instances'''
        reestablish = lambda connector: connector.reestablished_connection
        return list(map(reestablish, self._connectors))