from pathlib import PosixPath
import configparser
from typing import Dict, Optional
import logging
log = logging.getLogger(__name__)
MAIN_CONFIG_PATH = '~/.config/TensorHive/main_config.ini'


class ConfigLoader:
    @staticmethod
    def load(path, displayed_title=''):
        import configparser
        config = configparser.ConfigParser(strict=False)
        full_path = PosixPath(path).expanduser()
        if config.read(str(full_path)):
            log.info('[•] Reading {} config from {}'.format(displayed_title, path))
        else:
            log.warning('[✘] Missing configuration file ({})'.format(path))
            log.warning('Using default settings from config.py')
        return config


config = ConfigLoader.load(MAIN_CONFIG_PATH, displayed_title='main')


def display_config(cls):
    '''
    Displays all uppercase class atributes (class must be defined first)
    Example usage: display_config(API_SERVER)
    '''
    print('[{class_name}]'.format(class_name=cls.__name__))
    for key, value in cls.__dict__.items():
        if key.isupper():
            print('{} = {}'.format(key, value))


class SSH:
    section = 'ssh'
    HOSTS_CONFIG_FILE = config.get(section, 'hosts_config_file', fallback='~/.config/TensorHive/hosts_config.ini')
    TEST_ON_STARTUP = config.getboolean(section, 'test_on_startup', fallback=True)
    TIMEOUT = config.getfloat(section, 'timeout', fallback=10.0)
    NUM_RETRIES = config.getint(section, 'number_of_retries', fallback=1)
    

    def hosts_config_to_dict(path: str) -> Dict:
        '''Parses sections containing hostnames'''
        hosts_config = ConfigLoader.load(path, displayed_title='hosts')
        result = {}
        for section in hosts_config.sections():
            # We want to parse only sections which describe target hosts
            if section == 'proxy_tunneling':
                continue

            # TODO Handle more options (https://github.com/ParallelSSH/parallel-ssh/blob/2e9668cf4b58b38316b1d515810d7e6c595c76f3/pssh/clients/base_pssh.py#L119)
            hostname = section
            result[hostname] = {
                'user': hosts_config.get(hostname, 'user'),
                'port': hosts_config.getint(hostname, 'port', fallback=22)
            }
        return result

    def proxy_config_to_dict(path: str) -> Optional[Dict]:
        '''Parses [proxy_tunneling] section'''
        config = ConfigLoader.load(path, displayed_title='proxy')
        section = 'proxy_tunneling'

        # Check if section is present and if yes, check if tunneling is enabled
        if config.has_section(section) and config.getboolean(section, 'enabled', fallback=False):
            return {
                'proxy_host': config.get(section, 'proxy_host'),
                'proxy_user': config.get(section, 'proxy_user'),
                'proxy_port': config.getint(section, 'proxy_port', fallback=22)
            }
        else:
            return None

    AVAILABLE_NODES = hosts_config_to_dict(HOSTS_CONFIG_FILE)
    PROXY = proxy_config_to_dict(HOSTS_CONFIG_FILE)


class DB:
    section = 'database'
    default_path = '~/.config/TensorHive/database.sqlite'

    def uri_for_path(path: str) -> str:
        return 'sqlite:///{}'.format(PosixPath(path).expanduser())

    SQLALCHEMY_DATABASE_URI = uri_for_path(config.get(section, 'path', fallback=default_path))


class API:
    section = 'api'
    TITLE = config.get(section, 'title', fallback='TensorHive API')
    VERSION = config.getfloat(section, 'version', fallback=0.2)
    URL_PREFIX = config.get(section, 'url_prefix', fallback='api/{}'.format(VERSION))
    SPEC_FILE = config.get(section, 'spec_file', fallback='api_specification.yml')
    IMPL_LOCATION = config.get(section, 'impl_location', fallback='tensorhive.api.controllers')


class APP_SERVER:
    section = 'web_app.server'
    BACKEND = config.get(section, 'backend', fallback='gunicorn')
    HOST = config.get(section, 'host', fallback='0.0.0.0')
    PORT = config.getint(section, 'port', fallback=5000)
    WORKERS = config.getint(section, 'workers', fallback=4)
    LOG_LEVEL = config.get(section, 'loglevel', fallback='warning')


class API_SERVER:
    section = 'api.server'
    BACKEND = config.get(section, 'backend', fallback='gevent')
    HOST = config.get(section, 'host', fallback='0.0.0.0')
    PORT = config.getint(section, 'port', fallback=1111)
    DEBUG = config.getboolean(section, 'debug', fallback=False)


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


class AUTH:
    from datetime import datetime, timedelta
    # FIXME Refactor, use .ini instead
    FLASK_JWT = {
        'SECRET_KEY': 'jwt-some-secret',
        'JWT_BLACKLIST_ENABLED': True,
        'JWT_BLACKLIST_TOKEN_CHECKS': ['access', 'refresh'],
        'BUNDLE_ERRORS': True,
        'JWT_ACCESS_TOKEN_EXPIRES': datetime.utcnow() + timedelta(minutes=15),
        'JWT_REFRESH_TOKEN_EXPIRES': datetime.utcnow() + timedelta(days=30),
        'JWT_TOKEN_LOCATION': ['headers']
    }

