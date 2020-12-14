from pathlib import PosixPath
import configparser
from typing import Dict, Optional, Any, List
from inspect import cleandoc
import shutil
import tensorhive
import os
import logging
log = logging.getLogger(__name__)


class CONFIG_FILES:
    # Where to copy files
    # (TensorHive tries to load these by default)
    config_dir = PosixPath.home() / '.config/TensorHive'
    MAIN_CONFIG_PATH = str(config_dir / 'main_config.ini')
    HOSTS_CONFIG_PATH = str(config_dir / 'hosts_config.ini')
    MAILBOT_CONFIG_PATH = str(config_dir / 'mailbot_config.ini')

    # Where to get file templates from
    # (Clone file when it's not found in config directory)
    tensorhive_package_dir = PosixPath(__file__).parent
    MAIN_CONFIG_TEMPLATE_PATH = str(tensorhive_package_dir / 'main_config.ini')
    HOSTS_CONFIG_TEMPLATE_PATH = str(tensorhive_package_dir / 'hosts_config.ini')
    MAILBOT_TEMPLATE_CONFIG_PATH = str(tensorhive_package_dir / 'mailbot_config.ini')

    ALEMBIC_CONFIG_PATH = str(tensorhive_package_dir / 'alembic.ini')
    MIGRATIONS_CONFIG_PATH = str(tensorhive_package_dir / 'migrations')


class ConfigInitilizer:
    '''Makes sure that all default config files exist'''

    def __init__(self):
        # 1. Check if all config files exist
        all_exist = PosixPath(CONFIG_FILES.MAIN_CONFIG_PATH).exists() and \
            PosixPath(CONFIG_FILES.HOSTS_CONFIG_PATH).exists() and \
            PosixPath(CONFIG_FILES.MAILBOT_CONFIG_PATH).exists()

        if not all_exist:
            log.warning('[•] Detected missing default config file(s), recreating...')
            self.recreate_default_configuration_files()
        log.info('[•] All configs already exist, skipping...')

    def recreate_default_configuration_files(self) -> None:
        try:
            # 1. Create directory for stroing config files
            CONFIG_FILES.config_dir.mkdir(parents=True, exist_ok=True)

            # 2. Clone templates safely from `tensorhive` package
            self.safe_copy(src=CONFIG_FILES.MAIN_CONFIG_TEMPLATE_PATH, dst=CONFIG_FILES.MAIN_CONFIG_PATH)
            self.safe_copy(src=CONFIG_FILES.HOSTS_CONFIG_TEMPLATE_PATH, dst=CONFIG_FILES.HOSTS_CONFIG_PATH)
            self.safe_copy(src=CONFIG_FILES.MAILBOT_TEMPLATE_CONFIG_PATH, dst=CONFIG_FILES.MAILBOT_CONFIG_PATH)

            # 3. Change config files permission
            rw_owner_only = 0o600
            os.chmod(CONFIG_FILES.MAIN_CONFIG_PATH, rw_owner_only)
            os.chmod(CONFIG_FILES.HOSTS_CONFIG_PATH, rw_owner_only)
            os.chmod(CONFIG_FILES.MAILBOT_CONFIG_PATH, rw_owner_only)
        except Exception:
            log.error('[✘] Unable to recreate configuration files.')

    def safe_copy(self, src: str, dst: str) -> None:
        '''Safe means that it won't override existing configuration'''
        if PosixPath(dst).exists():
            log.info('Skipping, file already exists: {}'.format(dst))
        else:
            shutil.copy(src, dst)
            log.info('Copied {} to {}'.format(src, dst))


class ConfigLoader:
    @staticmethod
    def load(path, displayed_title=''):
        import configparser
        config = configparser.ConfigParser(strict=False)
        full_path = PosixPath(path).expanduser()
        if config.read(str(full_path)):
            log.info('[•] Reading {} config from {}'.format(displayed_title, full_path))
        else:
            log.warning('[✘] Configuration file not found ({})'.format(full_path))
            log.info('Using default {} settings from config.py'.format(displayed_title))
        return config


ConfigInitilizer()
config = ConfigLoader.load(CONFIG_FILES.MAIN_CONFIG_PATH, displayed_title='main')


def display_config(cls):
    '''
    Displays all uppercase class atributes (class must be defined first)
    Example usage: display_config(API_SERVER)
    '''
    print('[{class_name}]'.format(class_name=cls.__name__))
    for key, value in cls.__dict__.items():
        if key.isupper():
            print('{} = {}'.format(key, value))


def check_env_var(name: str):
    '''Makes sure that env variable is declared'''
    if not os.getenv(name):
        msg = cleandoc(
            '''
            {env} - undeclared environment variable!
            Try this: `export {env}="..."`
            ''').format(env=name).split('\n')
        log.warning(msg[0])
        log.warning(msg[1])


class SSH:
    section = 'ssh'
    HOSTS_CONFIG_FILE = config.get(section, 'hosts_config_file', fallback=CONFIG_FILES.HOSTS_CONFIG_PATH)
    TEST_ON_STARTUP = config.getboolean(section, 'test_on_startup', fallback=True)
    TIMEOUT = config.getfloat(section, 'timeout', fallback=10.0)
    NUM_RETRIES = config.getint(section, 'number_of_retries', fallback=1)
    KEY_FILE = config.get(section, 'key_file', fallback='~/.config/TensorHive/ssh_key')

    def hosts_config_to_dict(path: str) -> Dict:  # type: ignore
        '''Parses sections containing hostnames'''
        hosts_config = ConfigLoader.load(path, displayed_title='hosts')
        result = {}
        for section in hosts_config.sections():
            # We want to parse only sections which describe target hosts
            if section == 'proxy_tunneling':
                continue

            hostname = section
            result[hostname] = {
                'user': hosts_config.get(hostname, 'user'),
                'port': hosts_config.getint(hostname, 'port', fallback=22)
            }
        return result

    def proxy_config_to_dict(path: str) -> Optional[Dict]:  # type: ignore
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

    def uri_for_path(path: str) -> str:  # type: ignore
        return 'sqlite:///{}'.format(PosixPath(path).expanduser())

    SQLALCHEMY_DATABASE_URI = uri_for_path(config.get(section, 'path', fallback=default_path))
    TEST_DATABASE_URI = 'sqlite://'  # Use in-memory (before: sqlite:///test_database.sqlite)


class API:
    section = 'api'
    TITLE = config.get(section, 'title', fallback='TensorHive API')
    URL_HOSTNAME = config.get(section, 'url_hostname', fallback='0.0.0.0')
    URL_PREFIX = config.get(section, 'url_prefix', fallback='api')
    SPEC_FILE = config.get(section, 'spec_file', fallback='api_specification.yml')
    IMPL_LOCATION = config.get(section, 'impl_location', fallback='tensorhive.api.controllers')

    import yaml
    respones_file_path = str(PosixPath(__file__).parent / 'controllers/responses.yml')
    with open(respones_file_path, 'r') as file:
        RESPONSES = yaml.safe_load(file)


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
    NOTIFY_VIA_EMAIL = config.getboolean(section, 'notify_via_email', fallback=False)


class MAILBOT:
    mailbot_config = ConfigLoader.load(CONFIG_FILES.MAILBOT_CONFIG_PATH, displayed_title='mailbot')
    section = 'general'
    INTERVAL = mailbot_config.getfloat(section, 'interval', fallback=10.0)
    NOTIFY_INTRUDER = mailbot_config.getboolean(section, 'notify_intruder', fallback=True)
    NOTIFY_ADMIN = mailbot_config.getboolean(section, 'notify_admin', fallback=False)
    ADMIN_EMAIL = mailbot_config.get(section, 'admin_email', fallback=None)

    section = 'smtp'
    SMTP_LOGIN = mailbot_config.get(section, 'email', fallback=None)
    SMTP_PASSWORD = mailbot_config.get(section, 'password', fallback=None)
    SMTP_SERVER = mailbot_config.get(section, 'smtp_server', fallback=None)
    SMTP_PORT = mailbot_config.getint(section, 'smtp_port', fallback=587)

    section = 'template/intruder'
    INTRUDER_SUBJECT = mailbot_config.get(section, 'subject')
    INTRUDER_BODY_TEMPLATE = mailbot_config.get(section, 'html_body')

    section = 'template/admin'
    ADMIN_SUBJECT = mailbot_config.get(section, 'subject')
    ADMIN_BODY_TEMPLATE = mailbot_config.get(section, 'html_body')


class USAGE_LOGGING_SERVICE:
    section = 'usage_logging_service'
    default_path = '~/.config/TensorHive/logs/'

    def full_path(path: str) -> str:  # type: ignore
        return str(PosixPath(path).expanduser())

    ENABLED = config.getboolean(section, 'enabled', fallback=True)
    UPDATE_INTERVAL = config.getfloat(section, 'update_interval', fallback=2.0)
    LOG_DIR = full_path(config.get(section, 'log_dir', fallback=default_path))
    LOG_CLEANUP_ACTION = config.getint(section, 'log_cleanup_action', fallback=2)


class TASK_SCHEDULING_SERVICE:
    section = 'task_scheduling_service'
    ENABLED = config.getboolean(section, 'enabled', fallback=True)
    UPDATE_INTERVAL = config.getfloat(section, 'update_interval', fallback=30.0)
    STOP_TERMINATION_ATTEMPTS_AFTER = config.getfloat(section, 'stop_termination_attempts_after_mins', fallback=5.0)


class AUTH:
    from datetime import timedelta
    section = 'auth'

    def config_get_parsed(option: str, fallback: Any) -> List[str]:  # type: ignore
        '''
        Parses value for option from string to a valid python list.
        Fallback value is returned when anything goes wrong (e.g. option or value not present)

        Example .ini file, function called with arguments: option='some_option', fallback=None
        [some_section]
        some_option = ['foo', 'bar']

        Will return:
        ['foo', 'bar']
        '''
        import ast
        try:
            raw_arguments = config.get('auth', option)
            parsed_arguments = ast.literal_eval(raw_arguments)
            return parsed_arguments
        except (configparser.Error, ValueError):
            log.warning('Parsing [auth] config section failed for option "{}", using fallback value: {}'.format(
                option, fallback))
            return fallback

    FLASK_JWT = {
        'SECRET_KEY': config.get(section, 'secrect_key', fallback='jwt-some-secret'),
        'JWT_BLACKLIST_ENABLED': config.getboolean(section, 'jwt_blacklist_enabled', fallback=True),
        'JWT_BLACKLIST_TOKEN_CHECKS': config_get_parsed('jwt_blacklist_token_checks', fallback=['access', 'refresh']),
        'BUNDLE_ERRORS': config.getboolean(section, 'bundle_errors', fallback=True),
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=config.getint(section, 'jwt_access_token_expires_minutes',
                                                                    fallback=1)),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=config.getint(section, 'jwt_refresh_token_expires_days',
                                                                  fallback=1)),
        'JWT_TOKEN_LOCATION': config_get_parsed('jwt_token_location', fallback=['headers'])
    }
