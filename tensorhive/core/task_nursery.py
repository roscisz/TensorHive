from tensorhive.core import ssh
from tensorhive.core.ssh import HostsConfig, ProxyConfig, Hostname, Username
from pssh.clients.native import ParallelSSHClient
from typing import List, Optional, Dict
import time


__author__ = '@micmarty'
__all__ = [
    'ScreenCommandBuilder',
    'Task',
    'spawn',
    'terminate',
    'running'
]

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


def running(host: Hostname, user: Username) -> List[int]:
    config = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config)
    pattern = '.*tensorhive_task'
    command = ScreenCommandBuilder.get_active_sessions(pattern)
    output = ssh.run_command(client, command)
    stdout = ssh.get_stdout(host, output)
    if not stdout:
        return []

    # '4321.foobar_session' -> 4321
    pid_from_session_name = lambda name: int(name.split('.')[0])
    pids = [pid_from_session_name(line) for line in stdout.split('\n')]
    return pids


if __name__ == '__main__':
    # Quick testing: python -m tensorhive.core.task_nursery
    # FIXME Mock: Received data digested by API controller
    user = '155136mm'
    pkey_path = '~/.ssh/id_rsa'  # storage for public and private keys, common for all users
    tasks = [
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo $USER'),
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo b'),
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo c'),
        Task('galileo.eti.pg.gda.pl', 'sleep 20; echo d')
    ]
    # config = ssh.build_dedicated_config_for('galileo.eti.pg.gda.pl', user)
    # client = ssh.get_client(config)
    # [task.spawn(client) for task in tasks]
    print(running('galileo.eti.pg.gda.pl', user))
    # kill_all_screen_sessions('galileo.eti.pg.gda.pl', user, pkey_path)
    # distribute_tasks(user, pkey_path, tasks)
    # print('[Mock] Waiting for 20s...')
    # time.sleep(20)
    # terminate_tasks(user, pkey_path, tasks)
