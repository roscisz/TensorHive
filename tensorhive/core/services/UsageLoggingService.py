from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.utils.decorators.override import override
from tensorhive.core.utils.enums import LogFileCleanupAction
from tensorhive.core.services.Service import Service
from tensorhive.models.Reservation import Reservation
from typing import Dict, List, Optional, Union
from tensorhive.config import USAGE_LOGGING_SERVICE
from pathlib import PosixPath
import datetime
import time
import gevent
import json
import logging
log = logging.getLogger(__name__)

# TODO Move both to utils
def avg(data: List[Union[int, float]]) -> float:
    '''Calculates average from a list of values'''
    try:
        return sum(data) // len(data)
    except ZeroDivisionError:
        return float(-1)

def object_serializer(obj):
    '''
    All non-JSON-serializable classes must be handled explicitly
    Usage example: json.dump(..., default=object_serializer)
    '''
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    elif isinstance(obj, set):
        return list(obj)

class LogFileBrowser:
    pass

class JSONLogFile:
    '''
    Encapsulates JSON file operations
    TODO Handle exceptions
    '''
    def __init__(self, path: PosixPath) -> None:
        self.path = path

    def read(self) -> Dict:
        with self.path.open(mode='r') as file:
            return json.load(file)

    def write(self, data: Dict, **kwargs) -> None:
        with self.path.open(mode='w') as file:
            try:
                json.dump(data, file, **kwargs)
            except:
                raise

class Log:
    '''Represents ordinary JSON log file, alters original input data before persisting'''
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

    def __init__(self, data: Dict) -> None:
        self.data = data

    def updated_log(self, log_file: JSONLogFile) -> Dict:
        '''Reads a log file, returns its content plus new data'''
        log = log_file.read()

        log['name'] = self.data['name']
        log['index'] = self.data['index']

        mem_util = self.data['metrics']['mem_util']['value']
        gpu_util = self.data['metrics']['mem_util']['value']

        if gpu_util is not None and mem_util is not None:
            log['timestamps'].append(datetime.datetime.utcnow())
            log['metrics']['gpu_util']['values'].append(gpu_util)
            log['metrics']['mem_util']['values'].append(mem_util)
            # TODO Add more metrics
        else:
            err_msg = '`mem_util` or `gpu_util` is not supported by this GPU'
            # Append message only once
            if err_msg not in log['messages']:
                log['messages'].append(err_msg)
        return log

    def save(self, out_path: PosixPath) -> None:
        log_file = JSONLogFile(out_path)

        # If file is empty, initialize it with template
        if not log_file.path.exists():
            log_file.write(self.empty_log_file_format)

        # Overwrite log file with updated content
        updated_log_content = self.updated_log(log_file)
        log_file.write(updated_log_content, default=object_serializer)

        log.debug('Log file has been updated {}'.format(out_path))


class Summary:
    '''Represents small JSON log file, created when standard log file expires'''
    def __init__(self, in_path: PosixPath) -> None:
        self.in_path = in_path
        log_contents = JSONLogFile(self.in_path).read()
        self.summary = {
            # TODO May want to rewrite name, index, uuid, etc.
            'gpu_util_avg': avg(log_contents['metrics']['gpu_util']['values']),
            'mem_util_avg': avg(log_contents['metrics']['mem_util']['values'])
        }

    def save(self, out_path: PosixPath) -> None:
        try:
            JSONLogFile(out_path).write(self.summary)
        except:
            raise
        else:
            log.info('Summary generated from {}'.format(self.in_path))
            log.debug(self.summary)


class UsageLoggingService(Service):
    '''
    Responsible for:
    1. Gathering infrastracture data within active reservation time
    2. Storing data as files in suitable format and location
    3. Preparing short summary when reservation time ends
    3. Deleting log files when they become useless
    '''
    # What to do when log file is expired
    log_cleanup_action = USAGE_LOGGING_SERVICE.LOG_CLEANUP_ACTION

    # Default location for all log files
    log_dir = PosixPath(USAGE_LOGGING_SERVICE.LOG_DIR).expanduser()

    def __init__(self, interval=0.0):
        super().__init__()
        self.interval = interval
        self.log_dir.mkdir(parents=True, exist_ok=True)

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object

    @override
    def do_run(self):
        start_time = time.perf_counter()

        self.log_current_usage()
        self.handle_expired_logs()

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)

    def log_current_usage(self):
        '''Updates all log files related to current reservations'''
        current_reservations = Reservation.current_events()
        infrastructure = self.infrastructure_manager.infrastructure
        for reservation in current_reservations:
            filename = '{id}.json'.format(id=reservation.id)
            log_file_path = self.log_dir / filename
            try:
                gpu_data = self.extract_specific_gpu_data(uuid=reservation.protected_resource_id, infrastructure=infrastructure)
                Log(data=gpu_data).save(out_path=log_file_path)
            except Exception as e:
                log.error(e)

    def _clean_up_old_log_file(self, file: PosixPath):
        '''
        Triggers an action on expired/summarized log file
        depending on the value specified by self.log_cleanup_action
        '''
        action = self.log_cleanup_action
        assert LogFileCleanupAction(action)

        if action == LogFileCleanupAction.REMOVE:
            file.unlink()
            msg = 'Log file has been cleaned up.'
        elif action == LogFileCleanupAction.HIDE:
            new_name = file.parent / ('.' + file.name)
            file.rename(new_name)
            msg = 'Log file is now hidden.'
        elif action == LogFileCleanupAction.RENAME:
            new_name = file.parent / ('old_' + file.name)
            file.rename(new_name)
            msg = 'Log file has been renamed to {}.'.format(new_name.name)

        modification_time = datetime.datetime.fromtimestamp(file.lstat().st_mtime)
        log.info('{} (mtime: {}, after: {})'.format(msg, modification_time, self.log_expiration_time))

    def handle_expired_logs(self):
        '''
        Seeks for expired, ordinary JSON log files.
        Log file expires after given amount of time (self.log_expiration_time) 
        since its last modification and when corresponding reservation record 
        is also expired.

        If such file is found it generates summary file and cleans up the original log file.
        Summary filenames are like: summary_10.json
        '''
        time_now = datetime.datetime.utcnow()

        # Get all files within given directory
        # Accept only files like: 10.json
        for item in self.log_dir.glob('[0-9]*.json'):
            if item.is_file():
                try:
                    id_from_filename = int(item.stem)
                    reservation = Reservation.get(id=id_from_filename)

                    # Check if file and its corresponding reservation record are both expired
                    reservation_expired = reservation.ends_at < time_now

                    if reservation_expired:
                        # Generate summary immidiately
                        summary_file_path = item.parent / 'summary_{old_name}'.format(old_name=item.name)
                        Summary(in_path=item).save(out_path=summary_file_path)

                        # Clean up log immidiately
                        self._clean_up_old_log_file(file=item)
                except:
                    break

    def extract_specific_gpu_data(self, uuid: str, infrastructure: Dict) -> Dict:
        '''Returns whole right-hand side value (dictionary) for given key (uuid)'''
        assert isinstance(infrastructure, dict)
        assert isinstance(uuid, str) and len(uuid) == 40

        for hostname in infrastructure.keys():
            gpu_data = infrastructure[hostname].get('GPU').get(uuid)
            if gpu_data:
                return gpu_data
        raise KeyError(uuid + ' has not been found!')
