from tensorhive.core import ssh
from tensorhive.core.ssh import HostsConfig, ProxyConfig, Hostname, Username
from pssh.clients.native import ParallelSSHClient
from typing import List, Optional, Dict
import time
import logging
from datetime import datetime
log = logging.getLogger(__name__)

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
    def spawn(command: str, session_name: str, capture_output=True, keep_alive=False) -> str:
        """Command that runs inside daemonized screen session.

        Command is put into background manually (-D + & instead of simply usin -d) -> we want to know the PID
        Ways to capture output:
            * standard way: keep session alive, user resumes and inspects it by himself.
                May need to use some workarounds if we want to know when command stops.
            * alternative way: screen should run ``script some_output.log -c "sleep 20; echo TensorHive"`
            * tee way (implemented here): redirect command's output from within screen with tee
                When used with -i, --ignore-interrupts options it won't accept SIGINT so that
                the main command will catch it instead of tee. Use case for this is when your command
                prints something important after SIGINT and you want to see it + put that into log file.
            * the screen way: use `screen -L -Logfile name.log`, unfortunately not all versions supports that feature...

        Side effects (incompatible with capture_output=True):
            * keep_alive will prevent saving command's output to log file.
            It is advised to keep this turned off, unless you really want to keep session
            alive even when the command has finished execution - sometimes useful!
        """
        if capture_output:
            if keep_alive:
                log.debug('keep_alive is set to False - incompatible with capture_output=True')
                keep_alive = False
            create_logfile_command = ScreenCommandBuilder.tmp_log_file()
            capturing_command = '| tee --ignore-interrupts $({})'.format(create_logfile_command)

        return 'screen -Dm -S {sess_name} bash -c "{cmd}{keep_alive} {log}" {to_bg}'.format(
            sess_name=session_name,  # will help distinguishing between TensorHive and user's sessions
            cmd=command,
            log=capturing_command if capture_output else '',  # see method description
            keep_alive='; exec sh' if keep_alive else '',  # prevents screen from terminating session when command finished executing
            to_bg='& echo $!'  # will print process pid
        )

    @staticmethod
    def tmp_log_file() -> str:
        """Command that creates tmp file for storing log content.

        Target directory is created automatically.
        Current implementation uses week number for easier differentiation.
        """
        target_dir = '~/TensorHiveLogs'
        week_no = datetime.today().strftime('%U')  # type: str
        name_template = 'week_' + week_no + '_XXXX'  # at least 3 'X' are required by mktemp
        return 'mkdir --parents {target_dir} && mktemp {target_dir}/{name_template} --suffix .log'.format(
            target_dir=target_dir, name_template=name_template
        )

    # TODO Use me instead of terminate?
    @staticmethod
    def interrupt(pid: int) -> str:
        """Command that sends SIGINT to screen session. Should be used to gracefully terminate running command."""
        return 'screen -S {} -X stuff $\'\cc\''.format(pid)

    @staticmethod
    def terminate(pid: int) -> str:
        """Command that terminates screen session using only pid (we don't need the full name: 1234.tensorhive)."""
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
