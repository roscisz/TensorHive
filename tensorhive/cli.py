import click
from tensorhive.core.utils.colors import orange, green
import tensorhive
import logging
import sys
'''
Current CLI Structure: (update regularly)
tensorhive
├── -v/--version
├── -u/--add-user
├── --log-level <level> (e.g. debug, info, warning, error, critical)
└── create
    └── user
        └── --multiple
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


def setup_logging(log_level=logging.INFO):
    FORMAT = '%(levelname)-8s | %(asctime)s | %(threadName)-30s | MSG: %(message)-79s | FROM: %(name)s'

    # Remove existing configuration first (otherwise basicConfig won't be applied for the second time)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # TODO May want to add file logger
    # TODO May want use dictConfig instead of basicConfig (must import separately: logging.config)

    # Apply new config
    logging.basicConfig(level=log_level, format=FORMAT)

    # May want to restrict logging from external modules (must be imported first!)
    # import pssh
    logging.getLogger('passlib').setLevel(logging.CRITICAL)
    logging.getLogger('pssh').setLevel(logging.CRITICAL)
    logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
    logging.getLogger('connexion').setLevel(logging.CRITICAL)
    logging.getLogger('swagger_spec_validator').setLevel(logging.CRITICAL)

    # May want to disable logging completely
    # logging.getLogger('werkzeug').disabled = True

    # Colored logs can be easily disabled by commenting this single line
    import coloredlogs
    coloredlogs.install(level=log_level, fmt=FORMAT)


def log_level_mapping(ctx, param, value: str) -> int:
    '''
    Callback function which takes care of mapping
    from cli string param to int log level
    '''
    if value is None:
        return logging.INFO
    return AVAILABLE_LOG_LEVELS[value]


@click.group(invoke_without_command=True)
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print the current version number and exit.')
@click.option('--log-level', '-l',
              type=click.Choice(AVAILABLE_LOG_LEVELS.keys()),
              callback=log_level_mapping,
              help='Log level to apply.')
# TODO Allow using custom configuration from file: --config
@click.pass_context
def main(ctx, log_level):
    if ctx.invoked_subcommand is not None:
        # Invoke subcommand only
        return

    click.echo('TensorHive {}'.format(tensorhive.__version__))
    setup_logging(log_level)

    from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
    from tensorhive.api.APIServer import APIServer
    from tensorhive.database import init_db
    from tensorhive.models.User import User
    from tensorhive.app.web.AppServer import start_server
    from multiprocessing import Process

    try:
        init_db()
        if User.query.count() == 0:
            prompt_to_create_first_account()

        manager = TensorHiveManager()
        api_server = APIServer()
        webapp_server = Process(target=start_server)

        manager.configure_services_from_config()
        manager.init()
        webapp_server.start()       # Separate process
        api_server.run_forever()    # Will block (runs on main thread)
    except KeyboardInterrupt:
        click.echo(orange('[⚙] Shutting down TensorHive...'))
        manager.shutdown()
        webapp_server.join()
        sys.exit()


@main.group()
def create():
    pass


@create.command()
@click.option('-m', '--multiple', is_flag=True, help='Create more users in one go.')
def user(multiple):
    from tensorhive.core.utils.AccountCreator import AccountCreator
    creator = AccountCreator()
    # Create one user
    creator.run_prompt()

    # Create more users
    while multiple:
        creator.run_prompt()


def prompt_to_create_first_account():
    '''
    Asks whether a user wants to create an account
    (called when the database has no users)
    '''
    from tensorhive.core.utils.AccountCreator import AccountCreator
    click.echo('Database has no users.')
    if click.confirm('Would you like to create a user account?', default=True):
        AccountCreator().run_prompt()
