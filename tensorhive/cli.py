import click
import tensorhive
from tensorhive.config import CONFIG
from tensorhive.config import LogConfig
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
    └── example
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
    from tensorhive.config import SERVICES_CONFIG
    
    LogConfig.apply(log_level)

    manager = TensorHiveManager()
    manager.configure_services(SERVICES_CONFIG.ENABLED_SERVICES)
    manager.start()

    click.echo('API server has started...')
    APIServer().start()

    manager.shutdown()
    manager.join()


@main.group()
@click.pass_context
def db(ctx):
    pass

@db.command()
@click.pass_context
def init(ctx):
    '''Initialize database'''
    from tensorhive.database import init_db
    click.echo('[•] Initializing database...')
    # TODO Check if init_db can fail and if so, print that error
    init_db()
    click.echo('[✔] Done.')

@db.command()
@click.pass_context
def example(ctx):
    '''Initialize dataSet'''
    from tensorhive.db_seeds import init_set
    click.echo('[•] Initializing data set...')
    init_set()
    click.echo('[✔] Done.')
