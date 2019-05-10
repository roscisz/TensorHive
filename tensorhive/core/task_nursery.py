from tensorhive.core import ssh
from tensorhive.core.ssh import HostsConfig, ProxyConfig, Hostname, Username
from pssh.clients.native import ParallelSSHClient
from typing import List, Optional, Dict, Iterator
import time
from datetime import datetime
import logging
log = logging.getLogger(__name__)

__author__ = '@micmarty'
__all__ = ['ScreenCommandBuilder', 'Task', 'spawn', 'terminate', 'running', 'fetch_log']


class ExitCodeError(AssertionError):
    pass


class SpawnError(Exception):
    pass


class ScreenCommandBuilder:
    """Set of configurable commands built on top of **screen** program."""

    @staticmethod
    def spawn(command: str,
              session_name: str,
              capture_output: bool = True,
              custom_log_name: Optional[str] = None,
              keep_alive: bool = False) -> str:
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

        Note: `custom_log_name` argument will be ignored when `capture_output=False`
        """
        if capture_output:
            if keep_alive:
                log.debug('keep_alive is set to False - incompatible with capture_output=True')
                keep_alive = False

            if custom_log_name:
                create_logfile_command = ScreenCommandBuilder.custom_log_file(custom_log_name)
            else:
                create_logfile_command = ScreenCommandBuilder.tmp_log_file()
            capturing_command = '| tee --ignore-interrupts $({})'.format(create_logfile_command)

        return 'screen -Dm -S {sess_name} bash -c "{cmd}{keep_alive} {log}" {to_bg}'.format(
            sess_name=session_name,  # will help distinguishing between TensorHive and user's sessions
            cmd=command,
            log=capturing_command if capture_output else '',  # see method description
            keep_alive='; exec sh'
            if keep_alive else '',  # prevents screen from terminating session when command finished executing
            to_bg='& echo $!'  # will print process pid
        )

    @staticmethod
    def mkdir(target_dir: str) -> str:
        return 'mkdir --parents ' + target_dir

    @staticmethod
    def tmp_log_file() -> str:
        """Command that creates tmp file for storing log content.

        When command is executed it will print path to newly created file.
        Target directory will be created automatically when executing.
        Current implementation uses week number for easier differentiation.
        """
        target_dir = '~/TensorHiveLogs'
        week_no = datetime.today().strftime('%U')  # type: str
        name_template = 'week_' + week_no + '_XXXX'  # at least 3 'X' are required by mktemp

        mkdir_cmd = ScreenCommandBuilder.mkdir(target_dir)
        mktemp_cmd = 'mktemp {dir}/{templ} --suffix .log'.format(dir=target_dir, templ=name_template)
        return mkdir_cmd + ' && ' + mktemp_cmd

    @staticmethod
    def custom_log_file(filename: str, target_dir: str = '~/TensorHiveLogs') -> str:
        """Command that prints path to custom log file (`filename`)

        Note: if log file already exists `tee` will overwrite it!
        Target directory will be created automatically when executing, but
        log file won't be created (`touch`ed), assuming that `tee` will create it when executing.
        """
        mkdir_cmd = ScreenCommandBuilder.mkdir(target_dir)
        echopath_cmd = 'echo {dir}/{name}.log'.format(dir=target_dir, name=filename)
        return mkdir_cmd + ' && ' + echopath_cmd

    # TODO Use me instead of terminate? (see `ScreenCommandBuilder.spawn` description)
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

    def spawn(self, client: ParallelSSHClient, name_appendix: Optional[str] = None) -> int:
        """Spawns defined command via ssh client.
        Returns:
            pid of the process
        """
        sess_name = 'tensorhive_task'
        log_name = None
        if name_appendix:
            sess_name += '_' + name_appendix
            log_name = 'task_' + name_appendix

        command = self._command_builder.spawn(
            self.command, session_name=sess_name, capture_output=True, custom_log_name=log_name, keep_alive=False)
        output = ssh.run_command(client, command)
        stdout = ssh.get_stdout(host=self.hostname, output=output)

        if not stdout:
            reason = output[self.hostname].exception
            raise ValueError('Unable to acquire pid from empty stdout, reason: {}'.format(reason))
        # FIXME May want to decouple it somehow
        # FIXME pop() may theoretically fail (never stumbled upon this issue)
        pid = stdout.split().pop()
        self.pid = int(pid)
        return self.pid

    '''
    Note: These two methods are nearly identical, but I wanted
    to keep them separate because of logging and adding specialized logic later
    '''

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

    def interrupt(self, client: ParallelSSHClient) -> int:
        """Interrupts the task gracefully by sending SIGINT signal

        Returns:
            exit code of the operation
        """
        assert self.pid, 'You must first spawn the task or provide pid manually.'
        command = self._command_builder.interrupt(self.pid)
        output = ssh.run_command(client, command)
        exit_code = output[self.hostname].exit_code
        return exit_code


def spawn(command: str, host: Hostname, user: Username, name_appendix: Optional[str] = None) -> int:
    config = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config)
    task = Task(host, command)
    try:
        pid = task.spawn(client, name_appendix)
    except ValueError as e:
        raise SpawnError('{} on {}@{} failed: {}'.format(command, user, host, e))
    else:
        log.debug('Command spawned, pid: {}'.format(pid))
        return pid


def terminate(pid: int, host: Hostname, user: Username, gracefully: bool = True) -> int:
    config = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config)
    task = Task(host, pid=pid)

    if gracefully:
        exit_code = task.interrupt(client)
    else:
        exit_code = task.terminate(client)
    return exit_code


def running(host: Hostname, user: Username) -> List[int]:
    config = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config)
    pattern = '.*tensorhive_task.*'
    command = ScreenCommandBuilder.get_active_sessions(pattern)
    output = ssh.run_command(client, command)
    stdout = ssh.get_stdout(host, output)
    if not stdout:
        return []

    # '4321.foobar_session' -> 4321
    pid_from_session_name = lambda name: int(name.split('.')[0])
    pids = [pid_from_session_name(line) for line in stdout.split('\n')]
    log.debug('Running pids: {}'.format(pids))
    return pids


def fetch_log(host: Hostname, user: Username, task_id: int, tail: bool = False) -> Iterator[str]:
    path = '~/TensorHiveLogs/task_{}.log'.format(task_id)
    program = 'tail' if tail else 'cat'
    command = '{} {}'.format(program, path)

    config = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config)
    output = ssh.run_command(client, command)

    if output[host].exception:
        # Propagage ssh exception
        raise output[host].exception
    if output[host].exit_code != 0:
        raise ExitCodeError(path)
    return output[host].stdout


if __name__ == '__main__':
    # Quick testing: python -m tensorhive.core.task_nursery
    # FIXME Mock: Received data digested by API controller
    # user = '155136mm'
    # pkey_path = '~/.ssh/id_rsa'  # storage for public and private keys, common for all users
    # tasks = [
    #     Task('galileo.eti.pg.gda.pl', 'sleep 20; echo $USER'),
    #     Task('galileo.eti.pg.gda.pl', 'sleep 20; echo b'),
    #     Task('galileo.eti.pg.gda.pl', 'sleep 20; echo c'),
    #     Task('galileo.eti.pg.gda.pl', 'sleep 20; echo d')
    # ]
    # config = ssh.build_dedicated_config_for('galileo.eti.pg.gda.pl', user)
    # client = ssh.get_client(config)
    # [task.spawn(client) for task in tasks]

    user = 'bwroblew'
    host = 'ai.eti.pg.gda.pl'
    'cd ~/Simulators/095; DISPLAY= ./CarlaUE4.sh Town04'
    import os
    while True:
        print('''
Select action:
1) List active TH screen sessions pids (no database)
2) Spawn command
3) Interrupt task with pid
4) Kill all screen sessions
Any other key to clear console
        ''')
        action = input()[0]
        if action == '1':
            print(running(host, user))
        elif action == '2':
            cmd = input('Command > ')
            pid = spawn(cmd, host, user)
            print('Spawned with PID: ', pid)
        elif action == '3':
            pid = input('PID > ')
            exit_code = terminate(pid, host, user, gracefully=True)
            print('Interruption exit_code: ', exit_code)
        elif action == '4':
            running_tasks = running(host, user)
            if not running_tasks:
                print('No running tasks')
            for task in running_tasks:
                print('Terminating: ', task)
                exit_code = terminate(task, host, user)
                print('Kill exit_code: ', exit_code)
        else:
            os.system('clear')
            continue
