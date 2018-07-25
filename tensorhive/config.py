import logging


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
    # Available backends: 'flask', 'gevent', 'tornado', 'aiohttp'
    SERVER_BACKEND = 'flask'
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 9876
    SERVER_DEBUG = False

    SPECIFICATION_FILE = 'api_specification.yml'
    # Indicates the location of folder containing api implementation (RustyResolver)
    VERSION_FOLDER = 'api_v1'
    TITLE = 'TensorHive API'


class SSHConfig():
    '''
    Replace with your own config, see docs:
    https://parallel-ssh.readthedocs.io/en/latest/advanced.html#per-host-configuration
    '''
    AVAILABLE_NODES = {
        #'example_host_0': {'user': 'example_username'},
        #'example_host_1': {'user': 'example_username'}
    }
    CONNECTION_TIMEOUT = 1.0
    CONNECTION_NUM_RETRIES = 0


class DBConfig():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tensorhive_dev.db'


class LogConfig():
    LEVEL = logging.INFO
    FORMAT = '%(levelname)-8s | %(asctime)s | %(threadName)-30s | MSG: %(message)-80s | FROM: %(name)s'

    @classmethod
    def apply(cls):
        # TODO May want to add file logger
        # TODO May want use dictConfig (must import separately: logging.config)
        logging.basicConfig(level=cls.LEVEL, format=cls.FORMAT)
        # logging.config.dictConfig(...)

        # May want to restrict logging from external modules (must be imported first!)
        # import pssh

        logging.getLogger('pssh').setLevel(logging.CRITICAL)
        logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        logging.getLogger('connexion').setLevel(logging.CRITICAL)
        logging.getLogger('swagger_spec_validator').setLevel(logging.CRITICAL)

        # May want to disable logging completely
        # logging.getLogger('werkzeug').disabled = True


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

        ], interval=1.0)
        # Add more services here
    ]


SERVICES_CONFIG = ServicesConfig()
