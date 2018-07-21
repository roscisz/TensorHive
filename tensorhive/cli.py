import click
import tensorhive
from tensorhive.config import CONFIG

'''
Current CLI Structure: (update regularly)

tensorhive 
├── -v/--version
├── --help
├── run
|   ├── --help
|   ├── core      
|   └── api
└── db
    └── init
'''


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('TensorHive {ver}'.format(ver=tensorhive.__version__))
    ctx.exit()


@click.group()
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print the current version number and exit.')
def main():
    pass


@main.command()
@click.pass_context
def run(ctx):
    from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
    from tensorhive.core.utils.SigShutdownHandler import SigShutdownHandler
    from tensorhive.api.APIServer import APIServer
    from tensorhive.config import SERVICES_CONFIG

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