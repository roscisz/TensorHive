from tensorhive.core.services.Service import Service
from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel
from tensorhive.core.utils.decorators.override import override
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from pssh.clients.native import ParallelSSHClient
from typing import Generator, Dict, List
import datetime
import time
import gevent
import logging
log = logging.getLogger(__name__)


class ProtectionService(Service):
    '''
    Periodically checks for violation of any reservation made
    Actions taken when violation is detected can be customized with custom behaviours
    '''
    infrastructure_manager = None
    connection_manager = None
    handler = None

    def __init__(self, handler, interval=0.0):
        super().__init__()
        self.interval = interval
        self.handler = handler

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object
        elif isinstance(injected_object, SSHConnectionManager):
            self.connection_manager = injected_object

    def node_tty_sessions(self, connection, username: str = '') -> Dict[str, str]:
        '''Executes shell command in order to fetch all active terminal sessions'''
        command = 'w --no-header {}'.format(username)
        output = connection.run_command(command)

        # FIXME Assumes that only one node is in connection
        for _, host_out in output.items(): 
            result = self._parse_output(host_out.stdout) 
        return result

    def _parse_output(self, stdout: Generator) -> Dict[str, str]:
        '''
        Transforms command output into a dictionary
        Assumes command was: 'w --no-header'
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
                'TTY': columns[1],
                'FROM': columns[2],
                'LOGIN': columns[3],
                'IDLE': columns[4],
                'JCPU': columns[5],
                'PCPU': columns[6],
                'WHAT': columns[7]
            }

        return [as_dict(line) for line in stdout_lines]

    @override
    def do_run(self):
        time_func = time.perf_counter
        start_time = time_func()

        # 1. Get list of current reservations
        #current_reservations = ReservationEventModel.current_events()

        # Mock (it only imitates result from database, it won't be a dict!)
        current_reservations = [
            {
                'node': {'hostname': 'localhost'},
                'user': {'username': 'UNPERMITTED_USERNAME_MOCK'}
            }
        ]

        unauthorized_sessions = []
        for reservation in current_reservations:
            # 1. Extract reservation info
            hostname = reservation['node']['hostname']
            username = reservation['user']['username']

            # 2. Establish connection to node and find all tty sessions
            node_connection = self.connection_manager.single_connection(hostname)
            node_sessions = self.node_tty_sessions(node_connection)

            # 3. Any session that does not belong to a priviliged user should be rembered
            for session in node_sessions:
                if session['USER'] != username:
                    unauthorized_sessions.append(session)

        if len(unauthorized_sessions) > 0:
            # 4. Execute handler's behaviour on unauthorized ttys
            self.handler.trigger_action(node_connection, unauthorized_sessions)

        end_time = time_func()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)
        waiting_time = time_func() - end_time
        total_time = execution_time + waiting_time
        log.info('ProtectionService loop took: {:.2f}s (waiting {:.2f}) = {:.2f}'.format(
            execution_time, waiting_time, total_time))
