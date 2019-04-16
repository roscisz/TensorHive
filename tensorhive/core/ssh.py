from typing import Optional, Dict
from pssh.clients.native import ParallelSSHClient
import pssh
from tensorhive.core.utils.decorators import memoize, timeit
import functools

__author__ = '@micmarty'
__all__ = [
    'get_client',
    'run_command',
    'get_stdout'
    'succeeded'
]

HostsConfig = Dict[str, str]
ProxyConfig = Dict[str, str]
Hostname = str
Username = str
CommandResult = Dict[Hostname, pssh.output.HostOutput]


def build_dedicated_config_for(host: Hostname, user: Username) -> HostsConfig:
    return {
        host: {
            'user': user,
            'pkey': '~/.ssh/id_rsa'  # TODO Read from config
        }
    }


@memoize
def get_client(config: HostsConfig, pconfig: Optional[ProxyConfig] = None, **kwargs) -> ParallelSSHClient:
    """Builds and returns an ssh client object for given configuration.

    Client is fetched directly from cache if identical arguments were used recently.
    # TODO May not be thread-safe
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
        **kwargs
    )


@timeit
def run_command(client: ParallelSSHClient, command: str) -> Optional[CommandResult]:
    """Executes identical command for all client's hosts.

    Will wait until all hosts complete the command execution or timeout is reached.
    # TODO Describe exceptions
    """
    # stop_on_errors -> allows others hosts to execute when one crashes, combine exceptions
    # output is like: (hostname, host_output)
    try:
        result = client.run_command(command, stop_on_errors=False)
        client.join(result)
    except pssh.exceptions.Timeout:
        print('Command `{}` reached time limit'.format(command))
        raise
    except pssh.exceptions.ProxyError as e:
        print('Could not connect to proxy server, reason: {}'.format(e))
        raise
    # FIXME Handle more exceptions (more detailed messages)
    except Exception as e:
        print(e)
        raise
    else:
        # print('Command `{}` finished'.format(command))
        return result


def get_stdout(host: Hostname, output: pssh.output.HostOutput) -> str:
    """Unwraps stdout generator for given hostname."""
    try:
        host_result = output[host]
        assert not host_result.exception
        assert host_result.stdout
        return '\n'.join(list(host_result.stdout))
    except (AssertionError, KeyError):
        raise
    except pssh.exceptions.Timeout:
        # TODO Log something
        # client.reset_output_generators(output)
        raise


def succeeded(host: Hostname, output: pssh.output.HostOutput) -> bool:
    """Checks whether command's output was executed without any exception and exit code was 0."""
    return (output.exception is None) and (output.exit_code == 0)
