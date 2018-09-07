import click
import tensorhive
from tensorhive.config import CONFIG
from tensorhive.config import LogConfig, SSHConfig
import logging
'''
Current CLI Structure: (update regularly)

tensorhive 
├── -v/--version
├── --help
├── run
|   ├── --help
|   └── --log-level <level> (e.g. debug, info, warning, error, critical)
└── db
    └── init
'''
AVAILABLE_LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('TensorHive {ver}'.format(ver=tensorhive.__version__))
    ctx.exit()


def log_level_mapping(ctx, param, value: str) -> int:
    '''
    Callback function which takes care of mapping
    from cli string param to int log level
    '''
    if value is None:
        return LogConfig.DEFAULT_LEVEL
    return AVAILABLE_LOG_LEVELS[value]


@click.group()
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print the current version number and exit.')
def main():
    pass


@main.command()
@click.option('--log-level', '-l',
              type=click.Choice(AVAILABLE_LOG_LEVELS.keys()),
              callback=log_level_mapping,
              help='Log level to apply.')
@click.pass_context
def run(ctx, log_level):
    # from gevent import monkey
    # monkey.patch_all()
    
    from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
    from tensorhive.api.APIServer import APIServer
    from tensorhive.config import SERVICES_CONFIG, SSH_CONFIG
    from tensorhive.database import init_db
    from tensorhive.app.web.AppServer import start_server
    from multiprocessing import Process
    click.echo('TensorHive {}'.format(tensorhive.__version__))

    LogConfig.apply(log_level)
    SSH_CONFIG.load_configuration_file()

    init_db()
    manager = TensorHiveManager()
    manager.configure_services(SERVICES_CONFIG.ENABLED_SERVICES)
    webapp_server = Process(target=start_server)
    api_server = APIServer()

    manager.start()
    webapp_server.start()
    api_server.start()

    manager.shutdown()
    webapp_server.join()
    manager.join()
