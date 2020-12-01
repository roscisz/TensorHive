
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core.services.Service import Service
from typing import List, Dict, Any
import time
import gevent
from tensorhive.core.utils.decorators import override
import logging
log = logging.getLogger(__name__)


class MonitoringService(Service):
    '''
    Periodically updates infrastructure
    Can be configured to use multiple monitors against nodes with available connection
    '''
    monitors = []  # type: List
    connections = []  # type: List
    infrastructure_manager = None

    def __init__(self, monitors, interval=0.0):
        super().__init__()
        self.monitors = monitors
        self.interval = interval

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object
        elif isinstance(injected_object, SSHConnectionManager):
            self.connection_manager = injected_object

    @override
    def do_run(self):
        # FIXME Time measurements can be abandoned in the future
        time_func = time.perf_counter
        start_time = time_func()

        for monitor in self.monitors:
            try:
                monitor.update(self.connection_manager.connections, self.infrastructure_manager)
            except Exception as e:
                log.warning('Exception in monitor {}: {}'.format(monitor, e))

        end_time = time_func()
        execution_time = end_time - start_time

        # Hold on until next interval
        if execution_time < self.interval:
            gevent.sleep(self.interval - execution_time)
        waiting_time = time_func() - end_time
        total_time = execution_time + waiting_time
        log.debug('MonitoringService loop took: {:.2f}s (waiting {:.2f}) = {:.2f}'.format(
            execution_time, waiting_time, total_time))
