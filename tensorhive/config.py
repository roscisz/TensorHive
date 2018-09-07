from pathlib import PosixPath
import configparser
import logging
log = logging.getLogger(__name__)
CONFIG_PATH = '/home/miczi/Projects/TensorHive_CleaningForRelease02/tensorhive/default_config.ini'

class ConfigLoader:
    @staticmethod
    def load(path):
        import configparser
        config = configparser.ConfigParser()
        if config.read(path):
            log.info('Reading configuration from {}'.format(path))
        else:
            print('Missing configuration file ({})'.format(path))
        return config
config = ConfigLoader.load(CONFIG_PATH)

class APIConfig():
    # Available backends: 'flask', 'gevent', 'tornado', 'aiohttp'
    SERVER_BACKEND = 'gevent'

    '''WARNING
    If you make any changes to host address or port, you need to:
    - update api URI for Vue web app at tensorhive/app/web/dev/src/config/index.js
    - rebuild web app (cd tensorhive/app/web/dev; rm -rf ../dist; npm run build)
    '''
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 1111
    SERVER_DEBUG = False

    SPECIFICATION_FILE = 'api_specification.yml'
    # Indicates the location of folder containing api implementation (RustyResolver)
    VERSION_FOLDER = 'tensorhive.api.controllers'
    TITLE = 'TensorHive API'
    VERSION = 0.2
    URL_PREFIX = 'api/{version}'.format(version=VERSION)


class WebAppConfig():
    SERVER_BACKEND = 'gunicorn'
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    SERVER_LOGLEVEL = 'warning'
    NUM_WORKERS = 8


class DB:
    section = 'database'
    def uri_for_path(path) -> str:
        return 'sqlite:///{}'.format(PosixPath(path).expanduser())

    SQLALCHEMY_DATABASE_URI = uri_for_path(config.get(section, 'path'))


class SSHConfig():
    CONFIG_PATH = '~/.config/TensorHive/ssh_config.ini'
    # TODO Refactor
    TEST_CONNECTIONS_ON_STARTUP = True
    CONNECTION_TIMEOUT = 1.0
    CONNECTION_NUM_RETRIES = 0
    AVAILABLE_NODES = {}

    def load_configuration_file(self):
        import configparser
        from pathlib import PosixPath
        log = logging.getLogger(__name__)

        # 1. Try reading the file
        config = configparser.ConfigParser()
        path = str(PosixPath(self.CONFIG_PATH).expanduser())

        if config.read(path):
            log.info('Reading ssh configuration from {}'.format(path))
        else:
            log.critical('Missing ssh configuration file ({})!'.format(path))

        # 2. Parse configuration file
        host_config = {}
        for hostname in config.sections():
            # TODO Handle more options (https://github.com/ParallelSSH/parallel-ssh/blob/2e9668cf4b58b38316b1d515810d7e6c595c76f3/pssh/clients/base_pssh.py#L119)
            username = config.get(hostname, 'user')
            host_config[hostname] = {
                'user': username
            }
        self.AVAILABLE_NODES = host_config


# class LogConfig():
#     DEFAULT_LEVEL = logging.INFO
#     FORMAT = '%(levelname)-8s | %(asctime)s | %(threadName)-30s | MSG: %(message)-79s | FROM: %(name)s'

#     @classmethod
#     def apply(cls, log_level):
#         # Remove existing configuration first (otherwise basicConfig won't be applied for the second time)
#         for handler in logging.root.handlers[:]:
#             logging.root.removeHandler(handler)

#         # TODO May want to add file logger
#         # TODO May want use dictConfig instead of basicConfig (must import separately: logging.config)

#         # Apply new config
#         logging.basicConfig(level=log_level, format=cls.FORMAT)

#         # May want to restrict logging from external modules (must be imported first!)
#         # import pssh
#         logging.getLogger('pssh').setLevel(logging.CRITICAL)
#         logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
#         logging.getLogger('connexion').setLevel(logging.CRITICAL)
#         logging.getLogger('swagger_spec_validator').setLevel(logging.CRITICAL)

#         # May want to disable logging completely
#         # logging.getLogger('werkzeug').disabled = True

#         # Colored logs can be easily disabled by commenting this single line
#         import coloredlogs
#         coloredlogs.install(level=log_level, fmt=cls.FORMAT)


# Objects to be imported by application modules
SSH_CONFIG = SSHConfig()
API_CONFIG = APIConfig()
APP_CONFIG = WebAppConfig()


class ServicesConfig():
    '''
    WARNING! This class must be defined after SSH_CONFIG
    because instances below are depending on it
    '''
    from tensorhive.core.services.MonitoringService import MonitoringService
    from tensorhive.core.services.ProtectionService import ProtectionService
    from tensorhive.core.monitors.Monitor import Monitor
    from tensorhive.core.monitors.GPUMonitoringBehaviour import GPUMonitoringBehaviour
    from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
    from tensorhive.core.violation_handlers.MessageSendingBehaviour import MessageSendingBehaviour
    ENABLED_SERVICES = [
        MonitoringService(monitors=[
            Monitor(GPUMonitoringBehaviour())
            # Add more monitors here

        ], interval=1.0),
        # Not production-ready
        ProtectionService(handler=ProtectionHandler(behaviour=MessageSendingBehaviour()),
                          interval=10.0)
        # Add more services here
    ]


SERVICES_CONFIG = ServicesConfig()
