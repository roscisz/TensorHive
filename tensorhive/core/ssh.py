from typing import Optional, Dict
from pssh.clients.native import ParallelSSHClient
import pssh
from tensorhive.core.utils.decorators import hashable_cache, timeit
import functools

__author__ = '@micmarty'
__all__ = [
    'get_client',
    'run_command',
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

def memoize(func):
    '''Decorator which enables caching function's return values when called with the exact same arguments.

    When decorated function is called with arguments that are already in cache (key exists) it won't be executed
    but cached value will be returned instead. All arguments are serlialized into a single string.

    Cached values can be inspected by: print(decorated_func.cache)

    Note:
    This is extremely rare and probably won't be exploited by accident :)
    1) key = basic_key
        foo(True) and foo('True') are cached under same key name
    2) key = bulletproof_key
        foo(True) and foo('True') will be treated separately (different key in dict)
    '''
    cache = func.cache = {}
    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        basic_key = str(args) + str(kwargs)
        cls_name = lambda val: val.__class__.__name__
        bulletproof_key = basic_key + str([cls_name(arg) for arg in args]) + str([cls_name(val) for val in kwargs.values()])
        key = bulletproof_key
        print(key)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return memoized_func

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
