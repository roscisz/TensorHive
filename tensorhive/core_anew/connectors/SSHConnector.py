import spur


class SSHConnector():

    def __init__(self, hostname, username):
        # TODO Add argument validation
        self._hostname = hostname
        self._username = username
    # TODO Add more parameters to SshShell call

    @property
    def reestablished_connection(self):
        '''
        Returns a new instance of shell every time
        (using 'with' clause calls __enter__ and __exit__ in spur, so that
        the instance once used, becomes unusable) 
        # TODO Maybe it would be beneficial not to close the shell after each single command that was run
        '''
        return spur.SshShell(
            hostname=self._hostname,
            username=self._username)
