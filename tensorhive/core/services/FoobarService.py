from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.utils.decorators.override import override
from tensorhive.core.services.Service import Service
from tensorhive.models.Reservation import Reservation
from typing import Dict, List, Optional, Union
from tensorhive.config import FOOBAR_SERVICE
from pathlib import PosixPath
import datetime
import time
import gevent
import json
import logging
log = logging.getLogger(__name__)

# TODO Move both to utils
def avg(data: List[Union[int, float]]) -> float:
    try:
        return sum(data) // len(data)
    except ZeroDivisionError:
        return float(-1)

def object_serializer(obj):
    '''All non-JSON-serializable classes must be handled explicitly'''
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    elif isinstance(obj, set):
        return list(obj)

class FoobarService(Service):
    '''
    Responsible for:
    1. Gathering infrastracture data within active reservation time
    2. Storing data as files in suitable format and location
    3. Preparing short summary when reservation time ends
    3. Deleting log files when they become useless
    '''
    # After that time, log file will be digested into summary file and then removed
    log_expiration_time = datetime.timedelta(minutes=1)

    # Template structure for .json log files
    empty_log_file_format = {
        'name': str(),
        'index': int(),
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
        # Create logging directory
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

        for reservation in current_reservations:
            try:
                gpu_data = self.extract_specific_gpu_data(uuid=reservation.protected_resource_id, infrastructure=infrastructure)
                self.dump_to_file(data=gpu_data, filename='{}.json'.format(reservation.id))
            except Exception as e:
                log.debug(e)

        self.handle_expired_logs()

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)

    def save_summary(self, path: PosixPath) -> bool:
        '''
        Makes a simple digest of given log file by calculating average resource usage.
        Returns wheter summary was successfully persisted or not.
        '''
        try:
            # 1. Prepare summary
            with path.open(mode='r') as file:
                log_contents = json.load(file)
                summary = {
                    # TODO May want to rewrite name, index, uuid, etc.
                    'gpu_util_avg': avg(log_contents['metrics']['gpu_util']['values']),
                    'mem_util_avg': avg(log_contents['metrics']['mem_util']['values'])
                }

            # 2. Persist summary
            summary_file_path = path.parent / 'summary_{old_name}'.format(old_name=path.name)
            with summary_file_path.open(mode='w') as file:
                json.dump(summary, file)
        except Exception as e:
            log.error(e)
            return False
        else:
            log.info('Summary has been successfully generated from {}'.format(path))
            log.debug(summary)
            return True

    def handle_expired_logs(self, dir: str = FOOBAR_SERVICE.LOG_DIR):
        '''TODO'''
        time_now = datetime.datetime.utcnow()

        # Get all files within given directory
        for item in PosixPath(dir).glob('*'):
            if item.is_file():
                # Get filename without extension for files like: 10.json
                try:
                    id_from_filename = int(item.stem)
                except ValueError:
                    # Ignore other file names
                    # FIXME It warns about summary files, e.g. summary_10.json
                    # log.warning('Invalid log file names found in: {}'.format(dir))
                    break
                else:
                    reservation = Reservation.get(id=id_from_filename)

                # Check if file and its corresponding reservation record are both expired
                modification_time = datetime.datetime.utcfromtimestamp(item.stat().st_mtime)
                log_expired = modification_time + self.log_expiration_time < time_now
                reservation_expired = reservation.ends_at < time_now

                # reservation_expired = True
                # log_expired = True
                if log_expired and reservation_expired:
                    if self.save_summary(path=item):
                        # Expired log file can be safely deleted
                        item.unlink()
                        log.info('Expired log has been removed (mod_time: {mtime} (UTC), after {time}): {path}'.format(mtime=modification_time, time=self.log_expiration_time, path=item))

    def extract_specific_gpu_data(self, uuid: str, infrastructure: Dict) -> Dict:
        assert isinstance(infrastructure, dict)
        assert isinstance(uuid, str) and len(uuid) == 40

        for hostname in infrastructure.keys():
            gpu_data = infrastructure[hostname].get('GPU').get(uuid)
            if gpu_data:
                return gpu_data
        raise KeyError(uuid + ' has not been found!')

    def dump_to_file(self, data: Dict, dst_dir: str = FOOBAR_SERVICE.LOG_DIR, filename: str = 'data.json'):
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
                log_contents['timestamps'].append(datetime.datetime.utcnow())
                log_contents['metrics']['gpu_util']['values'].append(gpu_util)
                log_contents['metrics']['mem_util']['values'].append(mem_util)
            else:
                err_msg = '`mem_util` or `gpu_util` is not supported on this GPU'
                if err_msg not in log_contents['messages']:
                    log_contents['messages'].append(err_msg)

        # 3. Overwrite old file
        with log_file_path.open(mode='w') as file:
            json.dump(log_contents, file, default=object_serializer)
            log.debug('Log file has been updated {}'.format(log_file_path))


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
