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

    def _format_output(self, stdout: Generator) -> Dict[str, str]:
        stdout_lines = list(stdout)  # type: List[str]
        assert stdout_lines, 'stdout is empty!'
        assert len(stdout_lines) > 1, 'stdout query result contains header only!'

        # Extract keys from nvidia-smi query result header
        header = stdout_lines[0]  # type: str
        header_keys = header.split()  # type: List[str]

        stdout_lines_without_header = stdout_lines[1:]  # type: List[str]

        all_sessions = []
        for line in stdout_lines_without_header:
            # Split line by whitespaces into columns
            columns = line.split()  # type: List[str]
            basic_dict_from_line = {
                'username': columns[0], 'session': columns[1]}
            all_sessions.append(basic_dict_from_line)
        return all_sessions

    def find_active_tty_sessions(self, connection) -> Dict[str, str]:
        '''Executes shell command in order to fetch all active terminal sessions'''
        command = 'who --users --heading'
        output = connection.run_command(command, stop_on_errors=True)
        connection.join(output)

        for host, host_out in output.items():
            active_sessions = self._format_output(host_out.stdout)
        return active_sessions

    @override
    def do_run(self):
        time_func = time.perf_counter
        start_time = time_func()

        # 1. Get list of current reservations
        current_reservations = ReservationEventModel.current_events()
        # Mock (should be extracted from current_reservations)
        __authorized_usage_collection = [
            {
                'node': {'host_config': {'localhost': {'user': 'miczi'}}},
                'user': {'username': 'foobar'}
            },
            {
                'node': {'host_config': {'localhost': {'user': 'miczi'}}},
                'user': {'username': 'miczi'}
            }
        ]
        # 2. On each node check if only a particular, entitled user has active processes (terminal sessions for simplification)
        for permission_ticket in __authorized_usage_collection:
            # Establish connection to node
            host_config = permission_ticket['node']['host_config']
            connection = ParallelSSHClient(
                hosts=host_config.keys(),
                host_config=host_config
            )
            active_sessions = self.find_active_tty_sessions(connection)
            # 3. Prepare a list of (node, user) that violate the restriction

            # 4. Trigger handler if violation has been found
            # Mock: All sessions violate (dev only)
            unauthorized_sessions = active_sessions
            self.handler.trigger_action(connection, unauthorized_sessions)
        

        end_time = time_func()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)
        waiting_time = time_func() - end_time
        total_time = execution_time + waiting_time
        log.info('ProtectionService loop took: {:.2f}s (waiting {:.2f}) = {:.2f}'.format(
            execution_time, waiting_time, total_time))
