from tensorhive.core import ssh
from tensorhive.core.ssh import HostsConfig, ProxyConfig, Hostname, Username
from pssh.clients.native import ParallelSSHClient
from typing import List, Optional, Dict
import time


__author__ = '@micmarty'
__all__ = [
    'ScreenCommandBuilder',
    'Task',
    'succeeded'
]

"""TODO Implement controller

Example request with tasks to the API:
{
    'userId': 20,
    'commandTemplate': 'CUDA_VISIBLE_DEVICES={CVD} train.py --task-id {TID}',
    'values': [
        {'hostname': 'galileo', 'CVD': 0, 'TID': 'ps'},
        {'hostname': 'galileo', 'CVD': 1, 'TID': 'worker'},
        {'hostname': 'galileo', 'CVD': 1, 'TID': 'worker'},
        {'hostname': 'galileo', 'CVD': 1, 'TID': 'worker'},
    ]
}
"""

class ScreenCommandBuilder:
    """Set of configurable commands built on top of **screen** program."""

    @staticmethod
    def spawn(command: str, session_name: str, capture_output=True, keep_alive=True) -> str:
        """Command that runs inside daemonized screen session.
        
        Command is put into background manually (-D + & instead of simply usin -d) -> we want to know the PID
        Ways to capture output:
            * standard way (implemented): keep session alive, user resumes and inspects it by himself.
                May need to use some workarounds if we want to know when command stops.
            * alternative way: screen should run ``script some_output.log -c "sleep 20; echo TensorHive"`
            * the screen way: use `screen -L -Logfile name.log`, unfortunately not all versions supports that feature...
        """
        return 'screen -Dm {log} -S {sess_name} bash -c "{cmd}{block}" {to_bg}'.format(
            log='-L' if capture_output else '',
            sess_name=session_name,
            cmd=command,
            block='; exec sh' if keep_alive else '',
            to_bg='& echo $!'
        )

    @staticmethod
    def terminate(pid: int) -> str:
        """Terminates screen session using only pid (we don't need the full name: 1234.tensorhive)."""
        return 'screen -X -S {} quit'.format(pid)

    @staticmethod
    def get_active_sessions(grep_pattern: str) -> List[str]:
        """Fetches the full names of screen sessions matching given grep pattern."""
        return 'screen -ls | cut -f 2 | sed -e "1d;$d" | grep -e "{}"'.format(grep_pattern)

class Task:
    """Represents task executed on one machine."""

    __slots__ = ['hostname', 'command', 'pid', '_command_builder']

    def __init__(self, hostname: str, command: str = None, pid: int = None):
        self.hostname = hostname
        self.command = command
        self.pid = pid
        self._command_builder = ScreenCommandBuilder

    def spawn(self, client: ParallelSSHClient) -> int:
        """Spawns defined command via ssh client.
        Returns:
            pid of the process
        """
        command = self._command_builder.spawn(self.command, session_name='tensorhive_task')
        output = ssh.run_command(client, command)
        stdout = ssh.get_stdout(host=self.hostname, output=output)

        # FIXME May want to decouple it somehow
        pid = stdout.split().pop()
        self.pid = int(pid)
        return self.pid

    def terminate(self, client: ParallelSSHClient) -> int:
        """Terminates the task using it's pid.
        
        Returns:
            exit code of the operation
        """
        assert self.pid, 'You must first spawn the task or provide pid manually.'
        command = self._command_builder.terminate(self.pid)
        output = ssh.run_command(client, command)
        exit_code = output[self.hostname].exit_code
        return exit_code

def spawn(command: str, host: Hostname, user: Username) -> int:
    config = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config)
    task = Task(host, command)
    pid = task.spawn(client)
    return pid

def terminate(pid: int, host: Hostname, user: Username) -> int:
    config = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config)
    task = Task(host, pid=pid)
    exit_code = task.terminate(client)
    return exit_code

# def running(hostname: str, username: str) -> List[]:
#     config = {
#         hostname: {
#             'user': username,
#             'pkey': '~/.ssh/id_rsa'  # TODO Read from config
#         }
#     }
#     client = ssh.get_client(config)
#     pattern = '.*tensorhive_'
#     command = ScreenCommandBuilder.get_active_sessions(pattern)
#     task = Task(hostname, command)
#     pid = task.spawn(client)
#     return pid

# FIXME Prototype functions thats need refactoring and decoupling
def kill_all_screen_sessions(host, user, pkey):
    config = {
        host: {
            'user': user,
            'pkey': pkey_path
        }
    }
    client = ssh.get_client(config)
    pattern = '.*tensorhive_'
    print('Killing screen sessions with names: {}'.format(pattern))
    command = ScreenCommandBuilder.get_active_sessions(pattern)
    output = ssh.run_command(client, command)
    stdout = ssh.get_stdout(host=tasks[-1].hostname, output=output)
    for line in stdout.split('\n'):
        try:
            pid = int(line.split('.')[0])
            command = ScreenCommandBuilder.terminate(pid)
            print('Killing session "{}"'.format(pid))
            output = ssh.run_command(client, command)
        except (ValueError, IndexError):
            pass


def distribute_tasks(user, pkey, tasks: List[Task]):
    for task in tasks:
        config = {
            task.hostname: {
                'user': user,
                'pkey': pkey_path
            }
        }
        # Run user's commands
        client = ssh.get_client(config)
        pid = task.spawn(client)
        print('Task spawned with PID=', pid)
    
    # From last client!
    command = ScreenCommandBuilder.get_active_sessions('tensorhive')
    output = ssh.run_command(client, command)
    stdout = ssh.get_stdout(host=tasks[-1].hostname, output=output)
    print(stdout)

def terminate_tasks(user, pkey, tasks: List[Task]):
    for task in tasks:
        config = {
            task.hostname: {
                'user': user,
                'pkey': pkey_path
            }
        }
        # Run user's commands
        client = ssh.get_client(config)
        exit_code = task.terminate(client)
        print('Task with PID={} has been terminated with exit_code={})'.format(task.pid, exit_code))

if __name__ == '__main__':
    # FIXME Mock: Received data digested by API controller
    user = 'someone'
    pkey_path = '~/.ssh/id_rsa' # storage for public and private keys, common for all users
    tasks = [
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo $USER'),
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo b'),
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo c'),
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo d')
    ]
    kill_all_screen_sessions('galileo.eti.pg.gda.pl', user, pkey_path)
    distribute_tasks(user, pkey_path, tasks)
    print('[Mock] Waiting for 20s...')
    time.sleep(20)
    terminate_tasks(user, pkey_path, tasks)