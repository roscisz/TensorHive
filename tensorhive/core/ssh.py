from tensorhive.core.utils.decorators import memoize, timeit
from pssh.clients.native import ParallelSSHClient
from typing import Optional, Dict
import functools
import pssh
import logging
log = logging.getLogger(__name__)

__author__ = '@micmarty'
__all__ = ['build_dedicated_config_for', 'get_client', 'run_command', 'get_stdout', 'succeeded']
"""
This module provides a universal and stateless API for SSH-related tasks.

Author's note:
It has similar functionality to `SSHConnectionManager` on purpose -
the goal is to gradually replace chunks of code where it's currently used
without breaking compatibility everywhere.
(SSHConnectionManager has unnecessary boilerplate and stateful behaviour).
"""

# Typing aliases
HostsConfig = Dict[str, str]
ProxyConfig = Dict[str, str]
Hostname = str
Username = str
CommandResult = Dict[Hostname, pssh.output.HostOutput]


def build_dedicated_config_for(host: Hostname, user: Username) -> HostsConfig:
    """Takes off the responsibility for building correct HostsConfig manually.

    This function is supposed to provide high-level interface for providing
    valid `config` parameter to `get_client()` function.
    """
    assert host and user, 'Arguments must not be None!'
    return {
        host: {
            'user': user,
            'pkey': '~/.ssh/id_rsa'  # TODO Read path from config files (see config.py)
        }
    }


@memoize
def get_client(config: HostsConfig, pconfig: Optional[ProxyConfig] = None, **kwargs) -> ParallelSSHClient:
    """Builds and returns an ssh client object for given configuration.

    Client is fetched directly from cache if identical arguments were used recently.
    """
    if pconfig is None:
        pconfig = {}

    return ParallelSSHClient(
        hosts=config.keys(),
        host_config=config,
        proxy_host=pconfig.get('proxy_host'),
        proxy_user=pconfig.get('proxy_user'),
        proxy_port=pconfig.get('proxy_port'),
        num_retries=0,
        **kwargs)


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
        return result


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
        log.error('Could not unwrap HostOutput object for'.format(host))
    except (TypeError, ):
        log.warning('Could not extract stdout for {}: {}'.format(host, output))
        return None
    except Exception as e:
        log.critical(e)
        # Base for all pssh exceptions: https://github.com/ParallelSSH/parallel-ssh/blob/master/pssh/exceptions.py
        # client.reset_output_generators(output)
        raise


def succeeded(host: Hostname, output: pssh.output.HostOutput) -> bool:
    """Checks whether command's output was executed without any exception and exit code was 0."""
    return (output.exception is None) and (output.exit_code == 0)
