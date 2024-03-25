from tensorhive.core.utils.decorators import memoize, timeit
from tensorhive.config import SSH
from pssh.clients.ssh import ParallelSSHClient
from pssh.exceptions import AuthenticationException
from typing import Optional, Dict, Tuple, Generator, List
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from pathlib import PosixPath
import pssh
from pssh.exceptions import PKeyFileError
import logging
log = logging.getLogger(__name__)

__author__ = '@micmarty, @roscisz'
"""
This module provides a universal and stateless API for SSH-related tasks.

Author's note:
It has similar functionality to `SSHConnectionManager` on purpose -
the goal is to gradually replace chunks of code where it's currently used
without breaking compatibility everywhere.
(SSHConnectionManager has unnecessary boilerplate and stateful behaviour).
"""

# Typing aliases
HostConfig = Dict[str, str]
HostsConfig = Dict[str, HostConfig]
ProxyConfig = Dict[str, str]
Hostname = str
Username = str
CommandResult = Dict[Hostname, pssh.output.HostOutput]


def build_dedicated_config_for(host: Hostname, user: Username) -> Tuple[HostsConfig, Optional[ProxyConfig]]:
    """Takes off the responsibility for building correct HostsConfig manually.

    This function is supposed to provide high-level interface for providing
    valid `config` and `pconfig` parameter to `get_client()` function.
    """
    assert host and user, 'Arguments must not be None!'
    assert host in SSH.AVAILABLE_NODES
    hosts_config = {
        host: {
            'user': user,
            'pkey': SSH.KEY_FILE,
            'port': SSH.AVAILABLE_NODES[host]['port']
        }
    }
    # Read config extracted from hosts_config.ini (proxy is common for all hosts)
    pconfig = SSH.PROXY
    return hosts_config, pconfig


@memoize
def get_client(config: HostsConfig, pconfig: Optional[ProxyConfig] = None, **kwargs) -> ParallelSSHClient:
    """Builds and returns an ssh client object for given configuration.

    Client is fetched directly from cache if identical arguments were used recently.
    """
    hostnames = list(config.keys())
    try:
        if pconfig is not None:
            client = ParallelSSHClient(
                hosts=hostnames,
                host_config=config,
                pkey=SSH.KEY_FILE,
                proxy_host=SSH.PROXY['proxy_host'],
                proxy_user=SSH.PROXY['proxy_user'],
                proxy_port=SSH.PROXY['proxy_port'],
                **kwargs
                # Ignore timeout and num_retires for proxy
            )
        else:
            client = ParallelSSHClient(
                hosts=hostnames,
                host_config=config,
                timeout=SSH.TIMEOUT,
                pkey=SSH.KEY_FILE,
                num_retries=0,
                **kwargs
            )
    except PKeyFileError as e:
        log.error('[✘] {}'.format(str(e)))
        return None
    else:
        return client


def run_command(client: ParallelSSHClient, command: str) -> CommandResult:
    """Executes identical command on all hosts attached to client.

    Will wait until all hosts complete the command execution or timeout is reached.
    Re-raises pssh exceptions.
    # TODO Handle more specific exceptions
    """
    # stop_on_errors -> allows others hosts to execute when one crashes, combine exceptions
    # output is like: (hostname, host_output)
    try:
        result = client.run_command(command, stop_on_errors=False)
        client.join(result)
    except pssh.exceptions.Timeout:
        log.warning('Command `{}` reached time limit'.format(command))
        raise
    except pssh.exceptions.ProxyError as e:
        log.error('Could not connect to proxy server, reason: {}'.format(e))
        raise
    except Exception as e:
        log.critical(e)
        raise  # FIXME Find out what throws this exception
    else:
        log.debug('Command `{}` finished'.format(command))
        ret: CommandResult = {}
        for host_output in result:
            ret[host_output.host] = host_output
        return ret


def get_stdout(host: Hostname, output: pssh.output.HostOutput) -> Optional[str]:
    """Unwraps stdout generator for given hostname.

    Re-raises exceptions that occured during command execution.
    Returns a single, usually multi-line string or None
    # TODO Handle more exceptions
    """
    try:
        host_result = output[host]
        if host_result.exception:
            raise host_result.exception
        return '\n'.join(list(host_result.stdout))
    except KeyError:
        log.error('Could not unwrap HostOutput object for {}'.format(host))
        raise
    except (TypeError, ):
        log.warning('Could not extract stdout for {}: {}'.format(host, output))
        return None
    except AuthenticationException:
        log.warning('Could not authenticate SSH connection for {}: {}'.format(host, output))
        return None
    except Exception as e:
        log.critical(e)
        # Base for all pssh exceptions: https://github.com/ParallelSSH/parallel-ssh/blob/master/pssh/exceptions.py
        # client.reset_output_generators(output)
        raise


def succeeded(host: Hostname, output: pssh.output.HostOutput) -> bool:
    """Checks whether command's output was executed without any exception and exit code was 0."""
    return (output.exception is None) and (output.exit_code == 0)


def generate_cert(path, replace=False):
    path.touch(mode=0o600, exist_ok=replace)
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        encoding=crypto_serialization.Encoding.PEM,
        format=crypto_serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=crypto_serialization.NoEncryption()
    )
    with open(path, 'wb') as encrypted_file:
        encrypted_file.write(private_key)
    return private_key


def init_ssh_key(path: PosixPath):
    if path.exists():
        with open(path, "rb") as key_file:
            key = crypto_serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
        log.info('[⚙] Using existing SSH key in {}'.format(path))
    else:
        key = generate_cert(path)
        log.info('[⚙] Generated SSH key in {}'.format(path))
    return key


def node_tty_sessions(connection) -> List[Dict]:
    '''Executes shell command in order to fetch all active terminal sessions'''
    command = 'who'
    output = connection.run_command(command)

    # FIXME Assumes that only one node is in connection
    for host_out in output:
        result = _parse_who_output(host_out.stdout)
    return result


def _parse_who_output(stdout: Generator) -> List[Dict]:
    '''
    Transforms command output into a dictionary
    Assumes command was: 'who | grep <username>'
    '''
    stdout_lines = list(stdout)  # type: List[str]

    # Empty stdout
    if stdout_lines is None:
        return None

    def as_dict(line):
        columns = line.split()
        return {
            # I wanted it to be more explicit and flexible (even if it could be done better)
            'USER': columns[0],
            'TTY': columns[1]
        }

    return [as_dict(line) for line in stdout_lines]
