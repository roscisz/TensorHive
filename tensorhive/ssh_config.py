class SSHConfig():
    '''
    Here you declare how TensorHive can connect to nodes via ssh.
    It will use that information in order to monitor and manage available resources.

    Replace with your own config, see docs:
    https://parallel-ssh.readthedocs.io/en/latest/advanced.html#per-host-configuration
    '''
    AVAILABLE_NODES = {
        # 'example_host_0': {'user': 'example_username'}
        # 'example_host_1': {'user': 'example_username'}
    }
    CONNECTION_TIMEOUT = 1.0
    CONNECTION_NUM_RETRIES = 0
