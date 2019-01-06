from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.utils.decorators.override import override
from tensorhive.core.services.Service import Service
from tensorhive.models.Reservation import Reservation
from typing import Dict, List, Optional
from tensorhive.config import FOOBAR_SERVICE
from pathlib import PosixPath
from datetime import datetime
import time
import gevent
import json
import logging
log = logging.getLogger(__name__)

class FoobarService(Service):
    '''
    Responsible for:
    1. Gathering infrastracture data within active reservation time
    2. Storing data as files in suitable format and location
    3. Preparing short summary when reservation time ends
    3. Deleting data when they become useless
    '''
    infrastructure_manager = None
    empty_log_file_format = {
        'name': None,
        'index': None,
        'messages': [],
        'timestamps': [],
        'metrics': {
            'gpu_util': {
                'values': [],
                'unit': '%'
            },
            'mem_util': {
                'values': [],
                'unit': '%'
            },
        }
    }

    def __init__(self, interval=0.0):
        super().__init__()
        self.interval = interval

        # Initialize dir for storing log files
        PosixPath(FOOBAR_SERVICE.LOG_DIR).mkdir(parents=True, exist_ok=True)

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object

    @override
    def do_run(self):
        start_time = time.perf_counter()

        current_reservations = Reservation.current_events()
        infrastructure = self.infrastructure_manager.infrastructure

        # TODO Add high-level logic here
        for reservation in current_reservations:
            try:
                gpu_data = self.extract_specific_gpu_data(uuid=reservation.protected_resource_id, infrastructure=infrastructure)
                self.dump_to_file(data=gpu_data, dst_dir=FOOBAR_SERVICE.LOG_DIR, filename='{}.json'.format(reservation.id))

            except Exception as e:
                log.error(e)
                
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)

    def save_summary(self, path: PosixPath) -> bool:
        '''
        Makes a simple log digest by calculating average usage values.
        Returns wheter summary was successfully persisted or not.
        '''
        # 1. Prepare summary
        with path.open(mode='r') as file:
            try:
                log_contents = json.load(file)
                # Mock
                log_contents['metrics']['gpu_util']['values'] = [10, 20, 30]
                log_contents['metrics']['mem_util']['values'] = []

                def avg(data: List[Union[int, float]]) -> float:
                    try:
                        return sum(data) // len(data)
                    except ZeroDivisionError:
                        return float(-1)

                summary = {
                    'gpu_util_avg': avg(log_contents['metrics']['gpu_util']['values']),
                    'mem_util_avg': avg(log_contents['metrics']['mem_util']['values'])
                }
            except FileNotFoundError:
                raise

        print(summary)


        # with path.open(mode='w') as file:
        #     # TODO Non-standard classes must be serialized manually here
        #     def _serialize_objects(obj):
        #         if isinstance(obj, datetime.datetime):
        #             return obj.__str__()
        #         elif isinstance(obj, set):
        #             return list(obj)
        #     json.dump(log_contents, file, default=_serialize_objects)
        #     log.debug('Log file has been updated {}'.format(log_file_path))
    def extract_specific_gpu_data(self, uuid: str, infrastructure: Dict) -> Dict:
        assert isinstance(infrastructure, dict)
        assert isinstance(uuid, str) and len(uuid) == 40

        for hostname in infrastructure.keys():
            gpu_data = infrastructure[hostname].get('GPU').get(uuid)
            if gpu_data:
                return gpu_data
        raise KeyError(uuid + ' has not been found!')

    def dump_to_file(self, data: Dict, dst_dir: str, filename: str = 'data.json'):
        log_file_path = PosixPath(dst_dir).expanduser() / filename

        # 1. Create and fill in empty log file if necessary
        if not log_file_path.exists():
            with log_file_path.open(mode='w') as file:
                json.dump(self.empty_log_file_format, file)
    
        # 2. Read log file contents and append new data to it
        with log_file_path.open(mode='r') as file:
            log_contents = json.load(file)

            # TODO Add more if necessary
            log_contents['name'] = data['name']
            log_contents['index'] = data['index']

            mem_util = data['metrics']['mem_util']['value']
            gpu_util = data['metrics']['mem_util']['value']

            if gpu_util is not None and mem_util is not None:
                log_contents['timestamps'].append(datetime.utcnow())
                log_contents['metrics']['gpu_util']['values'].append(gpu_util)
                log_contents['metrics']['mem_util']['values'].append(mem_util)
            else:
                err_msg = '`mem_util` or `gpu_util` is not supported on this GPU'
                if err_msg not in log_contents['messages']:
                    log_contents['messages'].append(err_msg)

        # 3. Overwrite old file
        with log_file_path.open(mode='w') as file:
            # TODO Non-standard classes must be serialized manually here
            def _serialize_objects(obj):
                if isinstance(obj, datetime):
                    return obj.__str__()
                elif isinstance(obj, set):
                    return list(obj)
            json.dump(log_contents, file, default=_serialize_objects)


        # except FileNotFoundError:
#             # Create empty file
#             log_file_path.open(mode='w')
#         except PermissionError:
#             log.error('You don\'t have the permission to open {}'.format(log_file_path))
#         except json.JSONDecodeError as e:
#             log.warning(e)
#         except Exception as e:
#             log.error('Unexpected error occured: ' + e)

    # def save_summary(self, ):
    #     raise NotImplementedError

    def remove_expired_logs(self):
        raise NotImplementedError
