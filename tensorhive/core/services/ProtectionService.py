from tensorhive.core.services.Service import Service
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from tensorhive.database import db_session  # pylint: disable=unused-import
from tensorhive.core.utils.decorators import override
from tensorhive.core.utils.time import utc2local
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from typing import Set, List, Optional, Dict
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

    def __init__(self, handlers, interval=0.0, strict_reservations=False):
        super().__init__()
        self.interval = interval
        self.violation_handlers = handlers
        self.strict_reservations = strict_reservations

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

    def gpu_attr(self, hostname: str, uuid: str, attribute='name') -> str:
        '''Fetches the value of 'name' or 'index' attributes for GPU with specific UUID'''
        infrastructure = self.infrastructure_manager.infrastructure
        all_gpus = infrastructure.get(hostname, {}).get('GPU', {})
        gpu = all_gpus.get(uuid, {})
        return gpu.get(attribute, '<not available>')

    def store_violation(self, storage: Dict[str, Dict], process: Dict, hostname: str,
                        reservation: Reservation, gpu_id: str):
        intruder = process['owner']

        reservation_data = {
            'OWNER_USERNAME': reservation.user.username if reservation else None,
            'OWNER_EMAIL': reservation.user.email if reservation else None,
            'END': utc2local(reservation.end) if reservation else None,  # type: ignore
            'GPU_UUID': gpu_id,
            'GPU_NAME': self.gpu_attr(hostname, gpu_id, attribute='name'),
            'GPU_ID': self.gpu_attr(hostname, gpu_id, attribute='index'),
            'HOSTNAME': hostname
        }

        if intruder not in storage:
            storage[intruder] = {
                'INTRUDER_USERNAME': intruder,
                'RESERVATIONS': [reservation_data],
                'VIOLATION_PIDS': {hostname: set([process['pid']])},
            }
        else:
            storage[intruder]['RESERVATIONS'].append(reservation_data)
            storage[intruder]['VIOLATION_PIDS'][hostname].add(process['pid'])

    @override
    def do_run(self):
        time_func = time.perf_counter
        start_time = time_func()

        current_infrastructure = self.infrastructure_manager.all_nodes_with_gpu_processes()
        for hostname in current_infrastructure:
            violations = {}
            for gpu_id in current_infrastructure[hostname]:
                processes = current_infrastructure[hostname][gpu_id]
                if self.strict_reservations or (processes is not None and len(processes)):
                    current_gpu_reservations = Reservation.current_events(gpu_id)
                    reservation = None
                    if len(current_gpu_reservations):
                        reservation = current_gpu_reservations[0]
                        if hostname is None or reservation.user is None:
                            continue

                        for process in processes:
                            if process['owner'] != reservation.user.username:
                                self.store_violation(violations, process, hostname, reservation, gpu_id)
                    elif self.strict_reservations:
                        for process in processes:
                            self.store_violation(violations, process, hostname, reservation, gpu_id)

            for intruder in violations:
                violation_data = violations[intruder]
                reservations = violation_data['RESERVATIONS']
                hostnames = set([reservation_data['HOSTNAME'] for reservation_data in reservations])
                violation_data['SSH_CONNECTIONS'] = {hostname: self.connection_manager.single_connection(hostname)
                                                     for hostname in hostnames}
                violation_data['GPUS'] = ',\n'.join(['{} - GPU{}: {}'.format(data['HOSTNAME'], data['GPU_ID'],
                                                                             data['GPU_NAME'])
                                                     for data in reservations])
                violation_data['OWNERS'] = ', '.join(['{} ({})'.format(data['OWNER_USERNAME'], data['OWNER_EMAIL'])
                                                      for data in reservations])

                for handler in self.violation_handlers:
                    try:
                        handler.trigger_action(violation_data)
                    except Exception as e:
                        log.warning('Error in violation handler: {}'.format(e))

        end_time = time_func()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)
        waiting_time = time_func() - end_time
        total_time = execution_time + waiting_time
        log.debug('ProtectionService loop took: {:.2f}s (waiting {:.2f}) = {:.2f}'.format(
            execution_time, waiting_time, total_time))
