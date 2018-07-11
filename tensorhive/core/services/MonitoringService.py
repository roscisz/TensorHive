
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core.services.Service import Service
from typing import List, Dict, Any
import time
from tensorhive.core.utils.decorators.override import override


class MonitoringService(Service):
    '''
    Periodically updates infrastructure
    Can be configured to use multiple monitors against nodes with available connection
    '''

    # FIXME Add _
    monitors: List
    connections: List
    infrastructure_manager: Any

    # TODO Configure from config or inject
    _polling_interval: float = 1.0

    def __init__(self, monitors):
        super().__init__()
        self.monitors = monitors

    @override
    def start(self):
        super().start()

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object
        elif isinstance(injected_object, SSHConnectionManager):
            self.connection_manager = injected_object

    def shutdown(self):
        super().shutdown()

    @override
    def do_run(self):
        # DEBUG print(f'{self.service_name} is working...')
        import time
        start = time.time()
        for monitor in self.monitors:
            monitor.update(self.connection_manager.connections)
            self.infrastructure_manager.update_infrastructure(monitor.gathered_data)
        end = time.time()
        #time.sleep(10.0 - (end-start))
        print(f'Monitoring service loop took: {end-start}s')