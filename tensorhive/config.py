from typing import Any, Dict, Union

# TODO Remove dict config and floow APICOnfig, SSHConfig convention


class BaseConfig():
    '''Contains ALL configuration constants'''
    StringOrInt = Union[str, int, bool]

    def __init__(self) -> None:
        # Put all keys with default values here...

        self.CONFIG = {
            'TH__ENABLE_API_SERVER': True,
            'TH__SERVER_HOSTNAME': 'localhost',
            'TH__SERVER_PORT': 31333,
            'TH__SLEEP_IN_S': 5
        }
    # TODO Make config read-only

    def __repr__(self):
        return self.CONFIG


class DevelopmentConfig(BaseConfig):
    '''Default config, can overwrite BaseConfig'''
    VERSION = 'v0.2'

    def __init__(self) -> None:
        super().__init__()


class ProductionConfig(BaseConfig):
    '''Production use only, can overwrite BaseConfig'''
    pass


class APIConfig():
    API_SERVER_PORT = 9876
    API_SPECIFICATION_FILE = 'api_specification.yml'
    # Indicates location of folder containing api implementation (RustyResolver)
    API_VERSION_FOLDER = 'api_v1'
    API_TITLE = 'TensorHive API'


class SSHConfig():
    # Replace with your own config, see docs:
    # https://parallel-ssh.readthedocs.io/en/latest/advanced.html#per-host-configuration
    AVAILABLE_NODES = {
        'localhost': { 'user': 'miczi'},
        'example_host_0': { 'user': '155136mm'},
        'example_host_1': { 'user': 's155136'}
    }
    # TODO Make use of it in SSHConnectionManager.py
    #CONNECTION_TIMEOUT = 10

class DBConfig():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tensorhive_dev.db'

# Object to be imported by application modules
CONFIG = DevelopmentConfig()
SSH_CONFIG = SSHConfig()
API_CONFIG = APIConfig()
DB_CONFIG = DBConfig()
