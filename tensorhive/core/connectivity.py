import paramiko


# TODO: consider channel limit on the connections
class ConnectionManager:
    def __init__(self):
        self.connections = dict()

    def ensure_connection(self, node):
        if node not in self.connections.keys():
            self.connections[node] = self.setup_ssh_client(node)
        return self.connections[node]

    def run_command(self, node, command):
        client = self.ensure_connection(node)
        client.exec_command(command)

    def shutdown_connections(self):
        for node in self.connections.keys():
            self.connections[node].close()

    def setup_ssh_client(self, node):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(node)
        return client

    def shutdown(self):
        print('Shutting down node connections...')
        for node in self.connections.keys():
            self.connections[node].close()
