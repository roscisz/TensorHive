from tensorhive.core import ssh
from tensorhive.core.ssh import HostsConfig, ProxyConfig, Hostname, Username
from pssh.clients.native import ParallelSSHClient
from typing import List, Optional, Dict, Iterator, Tuple
import time
from datetime import datetime
import logging
log = logging.getLogger(__name__)

__author__ = '@micmarty'
__all__ = ['ExitCodeError', 'SpawnError', 'spawn', 'terminate', 'running', 'fetch_log']
"""
This module provides functionality for spawning commands on host machines via ssh.
It's divided into 3 parts:
    1) command builder(s):
        Classes that hold a set of commands (as strings) which can be launched by task executor
        in order to achieve some result, e.g. `spawn` and `terminate`
        You can implement your own command builder that uses different backend, currently it's `screen` program.

    2) task executor:
        Launches commands provided by command builder.
        It contains core logic for e.g. spawning, terminating processes on remote hosts via ssh.

    3) stateless API functions:
        Provides high-level interface for operations on remote host, like:
        * spawning, terminating processes
        * getting info about running processes
        * log fetching


Author's note:
    1) The ONLY recommended way to use this module from outside is by using
    exposed API functions (see __all__)
    # TODO Write tests
"""


# Custom exception names
class ExitCodeError(AssertionError):
    pass


class SpawnError(Exception):
    pass


class ScreenCommandBuilder:
    """Set of configurable commands built on top of `screen` program."""

    @staticmethod
    def spawn(command: str,
              session_name: str,
              capture_output: bool = True,
              custom_log_name: Optional[str] = None,
              keep_alive: bool = False) -> str:
        """Command that runs inside daemonized screen session.

        Command is put into background manually (-D + & instead of simply using -d) -> we want to know the PID
        Ways to capture output:
            * standard way: keep session alive, user resumes and inspects it by himself.
                May need to use some workarounds if we want to know when command stops.
            * alternative way: screen should run ``script some_output.log -c "sleep 20; echo TensorHive"`
            * tee way (implemented here): redirect command's stdout + stderr from within `screen` with `tee`
                When used with -i, --ignore-interrupts options it won't accept SIGINT so that
                the main command will catch it instead of `tee`. Use case for this is when your command
                prints something important after SIGINT and you want to see it + put that into log file.
            * the screen way: use `screen -L -Logfile name.log`, unfortunately
                              not all `screen` versions supports that feature.

        Side effects (incompatible with capture_output=True):
            * keep_alive will prevent saving command's output to log file.
            It is advised to keep this turned off, unless you really want to keep session
            alive even when the command has finished execution - sometimes useful!

        Note: `custom_log_name` argument will be ignored when `capture_output=False`

        """
        if capture_output:
            if keep_alive:
                log.debug('Forcing keep_alive=False - incompatible with capture_output=True')
                keep_alive = False

            if custom_log_name:
                create_logfile_command = ScreenCommandBuilder.custom_log_file(custom_log_name)
            else:
                create_logfile_command = ScreenCommandBuilder.tmp_log_file()
            # | -> stdout only, |& -> stdout + stderr (Bash 4), 2>&1 (old Bash)
            capturing_command = '|& tee --ignore-interrupts $({})'.format(create_logfile_command)

        return 'screen -Dm -S {sess_name} bash -c "{cmd}{keep_alive} {log}" {to_bg}'.format(
            sess_name=session_name,  # will help distinguishing between TensorHive and user's sessions
            cmd=command,
            log=capturing_command if capture_output else '',  # see docstring
            keep_alive='; exec sh' if keep_alive else '',  # see docstring
            to_bg='& echo $!'  # force printing process pid
        )

    @staticmethod
    def mkdir(target_dir: str) -> str:
        """Command that creates any inexisting directory given in path"""
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

    @staticmethod
    def interrupt(pid: int) -> str:
        """Command that sends SIGINT to screen session. Should be used to gracefully terminate running command."""
        return 'screen -S {} -X stuff "^C"'.format(pid)

    @staticmethod
    def terminate(pid: int) -> str:
        """Command that terminates screen session using only pid (we don't need the full name: 1234.tensorhive)."""
        return 'screen -X -S {} quit'.format(pid)

    @staticmethod
    def kill(pid: int) -> str:
        """Command that kills screen session by pid.

        It should also wipe dead sessions. Note that `kill` exit code is returned!
        """
        return 'kill -9 {}; KILL_EXIT=$?; screen -wipe; (exit $KILL_EXIT)'.format(pid)

    @staticmethod
    def get_active_sessions(grep_pattern: str) -> str:
        """Fetches the full names of screen sessions matching given grep pattern."""
        return 'screen -ls | cut -f 2 | sed -e "1d;$d" | grep -e "{}"'.format(grep_pattern)


class Task:
    """Represents task executed on one machine."""

    __slots__ = ['hostname', 'command', 'pid', '_command_builder']

    def __init__(self, hostname: str, command: str = None, pid: int = None):
        self.hostname = hostname
        self.command = command
        self.pid = pid
        # Here you can replace with your own backend/command builder
        self._command_builder = ScreenCommandBuilder

    def spawn(self, client: ParallelSSHClient, name_appendix: Optional[str] = None) -> int:
        """Spawns command via ssh client.
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

    """
    Author's note: These three methods below are nearly identical, but I wanted
    to keep them separate in order to easily extend their logic in the future.
    """

    def terminate(self, client: ParallelSSHClient) -> int:
        """Terminates the task using it's pid.

        Returns exit code of the operation
        """
        assert self.pid, 'You must first spawn the task or provide pid manually.'
        command = self._command_builder.terminate(self.pid)
        output = ssh.run_command(client, command)
        exit_code = output[self.hostname].exit_code
        return exit_code

    def interrupt(self, client: ParallelSSHClient) -> int:
        """Interrupts the task gracefully by sending SIGINT signal

        Returns exit code of the operation
        """
        assert self.pid, 'You must first spawn the task or provide pid manually.'
        command = self._command_builder.interrupt(self.pid)
        output = ssh.run_command(client, command)
        exit_code = output[self.hostname].exit_code
        return exit_code

    def kill(self, client: ParallelSSHClient) -> int:
        """Kills the task using it's pid.

        Returns exit code of the operation
        """
        assert self.pid, 'You must first spawn the task or provide pid manually.'
        command = self._command_builder.kill(self.pid)
        output = ssh.run_command(client, command)
        exit_code = output[self.hostname].exit_code
        return exit_code


def spawn(command: str, host: Hostname, user: Username, name_appendix: Optional[str] = None) -> int:
    """Stateless, high-level interface for spawning process on remote host.

    name_appendix: string that will be attached to session name and log file name
        Example: appendix='99' will produce session='tensorhive_task_99', log='task_99.log'
    Returns pid of new process
    """
    config, pconfig = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config, pconfig)
    task = Task(host, command)
    try:
        pid = task.spawn(client, name_appendix)
    except ValueError as e:
        raise SpawnError('{} on {}@{} failed: {}'.format(command, user, host, e))
    else:
        log.debug('Command spawned, pid: {}'.format(pid))
        return pid


def terminate(pid: int, host: Hostname, user: Username, gracefully: Optional[bool] = True) -> int:
    """Stateless, high-level interface for terminating process on remote host.

    gracefully: determines how task will be stopped
        False:  SIGKILL - almost guaranteed termination, aggressive
        None:   SIGTERM - works in most cases, but rather aggresive
        True:   SIGINT - often does not work, but only this method allows for capturing logs when program is closing
    Returns exit code of termination operation, not running process
    """
    config, pconfig = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config, pconfig)
    task = Task(host, pid=pid)

    if gracefully is None:
        exit_code = task.terminate(client)
    elif gracefully is False:
        exit_code = task.kill(client)
    else:
        exit_code = task.interrupt(client)
    return exit_code


def running(host: Hostname, user: Username) -> List[int]:
    """Stateless, high-level interface for getting a list of running processes on remote host.

    Ignores sessions with names other than `pattern`
    Returns a list of pids
    """
    config, pconfig = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config, pconfig)
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


def fetch_log(host: Hostname, user: Username, task_id: int, tail: bool = False) -> Tuple[Iterator[str], str]:
    """Stateless, high-level interface for fetching log files from remote host.

    Seeks and reads files located under specific folder on remote host.
    Re-raises pssh exceptions.
    tail: whether to include full content or only last 10 lines
    """
    # TODO Path should be configurable from config files (see config.py)
    path = '~/TensorHiveLogs/task_{}.log'.format(task_id)
    program = 'tail' if tail else 'cat'
    command = '{} {}'.format(program, path)

    config, pconfig = ssh.build_dedicated_config_for(host, user)
    client = ssh.get_client(config, pconfig)
    output = ssh.run_command(client, command)

    if output[host].exception:
        # Propagage ssh exception
        raise output[host].exception
    if output[host].exit_code != 0:
        raise ExitCodeError(path)
    return output[host].stdout, path
