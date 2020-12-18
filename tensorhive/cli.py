import click
from tensorhive.core.utils.colors import orange, green
from tensorhive.core.utils.exceptions import ConfigurationException
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
    setup_logging(log_level=log_level)

    from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
    from tensorhive.api.APIServer import APIServer
    from tensorhive.database import check_if_db_exists, ensure_db_with_current_schema
    from tensorhive.models.User import User
    from tensorhive.app.web.AppServer import start_server
    from multiprocessing import Process

    try:
        if not check_if_db_exists():
            init()
        else:
            ensure_db_with_current_schema()

        manager = TensorHiveManager()
        api_server = APIServer()
        webapp_server = Process(target=start_server)

        manager.configure_services_from_config()
        manager.init()
    except ConfigurationException:
        sys.exit()

    try:
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


@main.command()
def test():
    from tensorhive.config import SSH
    from tensorhive.core.managers.TensorHiveManager import TensorHiveManager

    setup_logging(log_level=logging.INFO)

    if not SSH.AVAILABLE_NODES:
        click.echo('[!] Empty ssh configuration. Please check {}'.format(SSH.HOSTS_CONFIG_FILE))
    else:
        TensorHiveManager.test_ssh()


@main.command()
def init():
    """Entry point for semi-automatic configuration process."""
    from tensorhive.config import CONFIG_FILES
    from tensorhive.config import config as main_config
    from tensorhive.core.utils.AccountCreator import AccountCreator
    from inspect import cleandoc
    from tensorhive.database import ensure_db_with_current_schema
    from tensorhive.models.User import User
    from tensorhive.models.Group import Group
    from tensorhive.models.Restriction import Restriction
    setup_logging(log_level=logging.INFO)

    logging.info('[•] Initializing configuration...')

    # Exposed host
    if click.confirm('[1/3] Do you want TensorHive to be accessible to other users in your network?'):
        host = click.prompt(
            '[1/3] What is the public hostname/address of this node (which is visible by all end users)?')
    else:
        host = '0.0.0.0'
    main_config.set('api', 'url_hostname', host)
    with open(CONFIG_FILES.MAIN_CONFIG_PATH, 'w') as main_config_file:
        main_config.write(main_config_file)
    click.echo(green('[⚙] TensorHive will be accessible via: {}'.format(host)))

    ensure_db_with_current_schema()

    # First user account
    if User.query.count() == 0:
        if click.confirm('[2/3] ' + orange('Database has no users.') + ' Would you like to create an account now?',
                         default=True):
            AccountCreator().run_prompt()
    else:
        click.echo('[•] There are some users in the database already, skipping...')

    # Edit configs
    click.echo('[3/3] ' + green('Done ✔!') + ' Now you just need to adjust these configs to your needs:\n')
    click.echo(cleandoc('''
        (required) {hosts}
        (optional) {main}
        (optional) {mailbot}
    ''').format(hosts=orange(CONFIG_FILES.HOSTS_CONFIG_PATH), main=CONFIG_FILES.MAIN_CONFIG_PATH,
                mailbot=CONFIG_FILES.MAILBOT_CONFIG_PATH))


@main.command()
def key():
    """Shows public key used for SSH authorization with nodes."""
    from tensorhive.config import SSH
    from tensorhive.core.ssh import init_ssh_key
    from pathlib import Path
    import os
    import platform

    key_path = Path(SSH.KEY_FILE).expanduser()
    private_key = init_ssh_key(key_path)
    public_key = private_key.get_base64()

    info_msg = '''
        This is the public key which will be used by TensorHive to reach your configured nodes via SSH,
        and allow for running remote tasks.
        Make sure that all nodes you've defined in ~/.config/TensorHive/hosts_config.ini know that key:
        just copy and paste it into ~/.ssh/authorized_keys on each target node.

    '''
    authorized_keys_entry = 'ssh-rsa {pub_key} {username}@{hostname}'.format(
        pub_key=public_key,
        username=os.environ['USER'],
        hostname=platform.node()
    )
    click.echo(info_msg)
    click.echo(authorized_keys_entry)


@create.command()
@click.option('-m', '--multiple', is_flag=True, help='Create more users in one go.')
def user(multiple):
    from tensorhive.core.utils.AccountCreator import AccountCreator
    setup_logging()
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
