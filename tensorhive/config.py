from pathlib import PosixPath
import configparser
import logging
log = logging.getLogger(__name__)
CONFIG_PATH = '~/.config/TensorHive/default_config.ini'

class ConfigLoader:
    @staticmethod
    def load(path):
        import configparser
        config = configparser.ConfigParser(strict=False)
        full_path = PosixPath(path).expanduser()
        if config.read(str(full_path)):
            log.info('Reading configuration from {}'.format(path))
        else:
            log.warning('Missing configuration file ({})'.format(path))
            log.warning('Using defaults defined in config.py')
        return config

config = ConfigLoader.load(CONFIG_PATH)

def display_config(cls):
    '''
    Displays all uppercase class atributes
    Example usage: display_config(API_SERVER)
    '''
    print('[{class_name}]'.format(class_name=cls.__name__))
    for key, value in cls.__dict__.items():
        if key.isupper():
            print('{} = {}'.format(key, value))

class API_SERVER:
    section = 'api.server'
    BACKEND = config.get(section, 'backend', fallback='gevent')
    HOST = config.get(section, 'host', fallback='0.0.0.0')
    PORT = config.getint(section, 'port', fallback=1111)
    DEBUG = config.getboolean(section, 'debug', fallback=False)

class API:
    section = 'api'
    TITLE = config.get(section, 'title', fallback='TensorHive API')
    VERSION = config.getfloat(section, 'version', fallback=0.2)
    URL_PREFIX = config.get(section, 'url_prefix', fallback='api/{}'.format(VERSION))
    SPEC_FILE_PATH = config.get(section, 'spec_file_path', fallback='api_specification.yml')
    IMPL_LOCATION = config.get(section, 'impl_location', fallback='tensorhive.api.controllers')

class DB:
    section = 'database'
    default_path = '~/.config/TensorHive/database.sqlite'

    def uri_for_path(path) -> str:
        return 'sqlite:///{}'.format(PosixPath(path).expanduser())

    SQLALCHEMY_DATABASE_URI = uri_for_path(config.get(section, 'path', fallback=default_path))

class APP_SERVER:
    section = 'web_app.server'
    BACKEND = config.get(section, 'backend', fallback='gunicorn')
    HOST = config.get(section, 'host', fallback='0.0.0.0')
    PORT = config.getint(section, 'port', fallback=5000)
    WORKERS = config.getint(section, 'workers', fallback=4)
    LOG_LEVEL = config.get(section, 'loglevel', fallback='warning')

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
SSH_CONFIG = SSHConfig()

class MONITORING_SERVICE:
    section = 'monitoring_service'
    ENABLED = config.getboolean(section, 'enabled', fallback=True)
    ENABLE_GPU_MONITOR = config.getboolean(section, 'enable_gpu_monitor', fallback=True)
    UPDATE_INTERVAL = config.getfloat(section, 'update_interval', fallback=2.0)


class PROTECTION_SERVICE:
    section = 'protection_service'
    ENABLED = config.getboolean(section, 'enabled', fallback=True)
    UPDATE_INTERVAL = config.getfloat(section, 'update_interval', fallback=2.0)
    NOTIFY_ON_PTY = config.getboolean(section, 'notify_on_pty', fallback=True)
