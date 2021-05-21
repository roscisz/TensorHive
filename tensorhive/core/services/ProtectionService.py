from tensorhive.core.services.Service import Service
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from tensorhive.database import db_session  # pylint: disable=unused-import
from tensorhive.core.utils.decorators import override
from tensorhive.core.utils.time import utc2local
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core import ssh
from typing import List, Optional
import time
import gevent
import json
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

    def find_hostname(self, uuid: str) -> Optional[str]:
        '''Seeks the hostname of node which has GPU with given UUID'''
        infrastructure = self.infrastructure_manager.infrastructure
        for hostname, node_data in infrastructure.items():
            if node_data.get('GPU', {}).get(uuid):
                return hostname
        log.warning('GPU with UUID="{}" was not found'.format(uuid))
        return None

    def gpu_users(self, node_processes, uuid) -> List[str]:
        '''Finds all users who are using GPU with given UUID'''
        owners = []
        gpu_processes = node_processes.get(uuid)

        # None -> GPU does not support `nvidia-smi pmon`
        if not gpu_processes:
            return []

        for process in gpu_processes:
            # FIXME: this if should be obsolete
            if process['command'] not in self.infrastructure_manager.ignored_processes:
                owners.append(process['owner'])
        unique_owners = list(set(owners))
        return unique_owners

    def gpu_attr(self, hostname: str, uuid: str, attribute='name') -> str:
        '''Fetches the value of 'name' or 'index' attributes for GPU with specific UUID'''
        infrastructure = self.infrastructure_manager.infrastructure
        all_gpus = infrastructure.get(hostname, {}).get('GPU', {})
        gpu = all_gpus.get(uuid, {})
        return gpu.get(attribute, '<not available>')

    @override
    def do_run(self):
        time_func = time.perf_counter
        start_time = time_func()

        # 1. Get list of current reservations
        current_reservations = Reservation.current_events()

        # FIXME DEBUG ONLY
        log.debug(json.dumps([r.as_dict() for r in current_reservations], indent=4))

        for reservation in current_reservations:
            # 1. Extract reservation info
            uuid = reservation.resource_id
            hostname = self.find_hostname(uuid)
            user = User.get(reservation.user_id)
            username = user.username
            if hostname is None or username is None:
                log.warning('Unable to process the reservation ({}@{}), skipping...'.format(username, hostname))
                continue

            # 2. Establish connection to node and find all tty sessions
            node_connection = self.connection_manager.single_connection(hostname)
            node_sessions = ssh.node_tty_sessions(node_connection)
            node_processes = self.infrastructure_manager.node_gpu_processes(hostname)
            reserved_gpu_process_owners = self.gpu_users(node_processes, uuid)

            is_unprivileged = lambda sess: sess['USER'] in reserved_gpu_process_owners
            intruder_ttys = [sess for sess in node_sessions if is_unprivileged(sess)]

            try:
                # Priviliged user can be ignored on this list
                reserved_gpu_process_owners.remove(username)
            except ValueError:
                pass
            finally:
                unprivileged_gpu_process_owners = reserved_gpu_process_owners

            # 3. Execute protection handlers
            for intruder in unprivileged_gpu_process_owners:
                violation_data = {
                    'INTRUDER_USERNAME': intruder,
                    'RESERVATION_OWNER_USERNAME': username,
                    'RESERVATION_OWNER_EMAIL': user.email,
                    'RESERVATION_END': utc2local(reservation.end),
                    'UUID': uuid,
                    'GPU_NAME': self.gpu_attr(hostname, uuid, attribute='name'),
                    'GPU_ID': self.gpu_attr(hostname, uuid, attribute='index'),
                    'HOSTNAME': hostname,
                    'TTY_SESSIONS': intruder_ttys,
                    'SSH_CONNECTION': node_connection
                }
                for handler in self.violation_handlers:
                    handler.trigger_action(violation_data)

        end_time = time_func()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)
        waiting_time = time_func() - end_time
        total_time = execution_time + waiting_time
        log.debug('ProtectionService loop took: {:.2f}s (waiting {:.2f}) = {:.2f}'.format(
            execution_time, waiting_time, total_time))
