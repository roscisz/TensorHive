import click

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
    click.echo(f'TensorHive {CONFIG.VERSION}')
    ctx.exit()


@click.group()
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print the current version number and exit.')
def main():
    pass


@main.group()
@click.pass_context
def run(ctx):
    '''What to run? Select one from the list specified below'''
    pass


@run.command()
@click.pass_context
def core(ctx):
    '''Start TensorHiveManager instance'''
    from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
    from tensorhive.core.services.MonitoringService import MonitoringService
    from tensorhive.core.monitors.GPUMonitor import GPUMonitor
    from tensorhive.core.utils.SigShutdownHandler import SigShutdownHandler
    
    termination_handler = SigShutdownHandler()
    services_to_inject = [MonitoringService(monitors=[GPUMonitor()
                                                      # Add more monitors here
                                                      ])
                          # Add more services here
                          ]

    manager = TensorHiveManager(services=services_to_inject)
    manager.start()
    while True:
        # time.sleep(CONFIG.TH__SLEEP_IN_S)

        if termination_handler.should_terminate:
            manager.shutdown()
            break
    manager.join()


@run.command()
@click.pass_context
def api(ctx):
    '''Start API server instance'''
    click.echo('API server has started...')
    from tensorhive.api.APIServer import APIServer
    APIServer().start()

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