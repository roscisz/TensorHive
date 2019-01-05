from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.utils.decorators.override import override
from tensorhive.core.services.Service import Service
from tensorhive.models.Reservation import Reservation
from typing import Dict, List
from pathlib import PosixPath
import time
import gevent
import json

class FoobarService(Service):
    main_log_dir = '~/.config/logs/{reservation_id}/'

    '''
    Responsible for:
    1. Gathering infrastracture data within active reservation time
    2. Storing data as files in suitable format and location
    3. Preparing short summary when reservation time ends
    3. Deleting data when they become useless
    '''
    infrastructure_manager = None

    def __init__(self, interval=0.0):
        super().__init__()
        self.interval = interval

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object

    @override
    def do_run(self):
        start_time = time.perf_counter()

        current_reservations = Reservation.current_events()
        infrastructure = self.infrastructure_manager.infrastructure

        for reservation in current_reservations:
            # TODO Add high-level logic

            # Initialize directory for storing logs
            final_log_dir = PosixPath.expanduser(self.main_log_dir) / str(reservation.protected_resource_id)
            final_log_dir.mkdir(parents=True, exist_ok=True)

            log_file_path = '{dir}/data.json'.format(dir=final_log_dir)
            with open(log_file_path, 'a') as file:
                json.dump(infrastructure, file)

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)

    def dump_to_file(self, data: Dict):
        raise NotImplementedError

    def save_summary(self, ):
        raise NotImplementedError

    def remove_expired_logs(self):
        raise NotImplementedError