from typing import Any, Dict, Union


class BaseConfig():
    '''Contains ALL configuration constants'''
    pass


class DevelopmentConfig(BaseConfig):
    '''Default config, can overwrite BaseConfig'''
    VERSION = 'v0.2'


class ProductionConfig(BaseConfig):
    '''Production use only, can overwrite BaseConfig'''
    pass


class APIConfig():
    API_SERVER_PORT = 9876
    API_SPECIFICATION_FILE = 'api_specification.yml'
    # Indicates location of a folder containing api implementation (RustyResolver)
    API_VERSION_FOLDER = 'api_v1'
    API_TITLE = 'TensorHive API'


class SSHConfig():
    '''
    Replace with your own config, see docs:
    https://parallel-ssh.readthedocs.io/en/latest/advanced.html#per-host-configuration
    '''
    AVAILABLE_NODES = {
        'localhost': {'user': 'miczi'},
        'example_host_0': {'user': '155136mm'},
        'example_host_1': {'user': 's155136'}
    }
    CONNECTION_TIMEOUT = 1
    CONNECTION_NUM_RETRIES = 0


class DBConfig():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tensorhive_dev.db'



# Objects to be imported by application modules
CONFIG = DevelopmentConfig()
SSH_CONFIG = SSHConfig()
API_CONFIG = APIConfig()
DB_CONFIG = DBConfig()


class ServicesConfig():
    '''
    WARNING! This class must be defined after SSH_CONFIG
    because instances below are depending on it
    '''
    from tensorhive.core.services.MonitoringService import MonitoringService
    from tensorhive.core.monitors.Monitor import Monitor
    from tensorhive.core.monitors.GPUMonitoringBehaviour import GPUMonitoringBehaviour
    ENABLED_SERVICES = [
        MonitoringService(monitors=[
            Monitor(GPUMonitoringBehaviour())
            # Add more monitors here
        ])
        # Add more services here
    ]


SERVICES_CONFIG = ServicesConfig()
