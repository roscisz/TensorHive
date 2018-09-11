from tensorhive.core.services.Service import Service
from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel
from tensorhive.models.user.UserModel import UserModel
from tensorhive.core.utils.decorators.override import override
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from pssh.clients.native import ParallelSSHClient
from typing import Generator, Dict, List, Optional
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
    violation_handlers = None

    def __init__(self, handlers, interval=0.0):
        super().__init__()
        self.interval = interval
        self.violation_handlers = handlers

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object
        elif isinstance(injected_object, SSHConnectionManager):
            self.connection_manager = injected_object

    def node_tty_sessions(self, connection) -> Dict[str, str]:
        '''Executes shell command in order to fetch all active terminal sessions'''
        command = 'who'
        output = connection.run_command(command)

        # FIXME Assumes that only one node is in connection
        for _, host_out in output.items():
            result = self._parse_output(host_out.stdout)
        return result

    def node_gpu_processes(self, hostname: str) -> Dict:
        '''

        Example result:
        {
            # Most common example
            "GPU-c6d01ed6-8240-2e11-efe9-aa32794b8273": [
                {
                    "pid": 1979,
                    "command": "X",
                    "owner": "root"
                }
            ],

            # If GPU has no processes
            "GPU-abcdefg6-8240-2e11-efe9-abcdefgb8273": [],

            # If GPU does not support `nvidia-smi pmon`
            "GPU-abcdefg6-8240-2e11-efe9-abcdefgb8273": None
        }
        '''
        infrastructure = self.infrastructure_manager.infrastructure

        # Make sure we can fetch GPU data first.
        # Example reasons: node is unreachable, nvidia-smi failed
        if infrastructure.get(hostname, {}).get('GPU') is None:
            log.debug('There is no GPU data for host: {}'.format(hostname))
            return {}

        # Loop through each GPU on node
        node_processes = {}
        for uuid, gpu_data in infrastructure[hostname]['GPU'].items():
            single_gpu_processes = infrastructure[hostname]['GPU'][uuid]['processes']
            node_processes[uuid] = single_gpu_processes
        return node_processes

    def _parse_output(self, stdout: Generator) -> Dict[str, str]:
        '''
        Transforms command output into a dictionary
        Assumes command was: 'who | grep <username>'
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
                'TTY': columns[1]
            }

        return [as_dict(line) for line in stdout_lines]

    def find_hostname(self, uuid: str) -> Optional[str]:
        '''Seeks the hostname of node which has GPU with given UUID'''
        infrastructure = self.infrastructure_manager.infrastructure
        for hostname, node_data in infrastructure.items():
            if node_data.get('GPU', {}).get(uuid):
                return hostname
        log.warning('GPU with UUID="{}" was not found'.format(uuid))
        return None

    @property
    def ignored_processes(self):
        return [
            '/usr/lib/xorg/Xorg',
            '/usr/bin/X',
            'X'
        ]

    def gpu_users(self, node_processes, uuid) -> List[str]:
        '''Finds all users who are using GPU with given UUID'''
        owners = []
        gpu_processes = node_processes.get(uuid)

        # None -> GPU does not support `nvidia-smi pmon`
        if not gpu_processes:
            return []

        for process in gpu_processes:
            if process['command'] not in self.ignored_processes:
                owners.append(process['owner'])
        unique_owners = list(set(owners))
        return unique_owners

    @override
    def do_run(self):
        time_func = time.perf_counter
        start_time = time_func()

        # 1. Get list of current reservations
        current_reservations = ReservationEventModel.current_events()

        # DEBUG ONLY
        __reservations_as_dict = [r.as_dict for r in current_reservations]
        import json
        log.debug(json.dumps(__reservations_as_dict, indent=4))

        for reservation in current_reservations:
            # 1. Extract reservation info
            uuid = reservation.resource_id
            hostname = self.find_hostname(uuid)
            username = UserModel.find_by_id(reservation.user_id).username
            if hostname is None or username is None:
                log.warning('Unable to process the reservation ({}@{}), skipping...'.format(username, hostname))
                continue

            # 2. Establish connection to node and find all tty sessions
            node_connection = self.connection_manager.single_connection(hostname)
            node_sessions = self.node_tty_sessions(node_connection)
            node_processes = self.node_gpu_processes(hostname)
            reserved_gpu_process_owners = self.gpu_users(node_processes, uuid)

            # 3. Any session that does not belong to a priviliged user should be remembered
            unauthorized_sessions = []
            for session in node_sessions:
                session_opened_by_unpriviliged_user = session['USER'] != username
                unpriviliged_user_has_active_gpu_processes = session['USER'] in reserved_gpu_process_owners
                if session_opened_by_unpriviliged_user and unpriviliged_user_has_active_gpu_processes:
                    # Inject additional data for handler
                    session['LEGITIMATE_USER'] = username
                    session['GPU_UUID'] = uuid
                    unauthorized_sessions.append(session)

            # 4. Execute handler's behaviour on unauthorized ttys
            if len(unauthorized_sessions) > 0:
                for handler in self.violation_handlers:
                    handler.trigger_action(node_connection, unauthorized_sessions)

        end_time = time_func()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)
        waiting_time = time_func() - end_time
        total_time = execution_time + waiting_time
        log.debug('ProtectionService loop took: {:.2f}s (waiting {:.2f}) = {:.2f}'.format(
            execution_time, waiting_time, total_time))
