import spur

class SSHConnector():
    # TODO add more parameters to SshShell call
    def shell_connection(self, hostname, username):
        return spur.SshShell(hostname=hostname, username=username)
