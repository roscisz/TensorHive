from tensorhive.core_anew.connectors.SSHConnector import SSHConnector
from tensorhive.core_anew.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core_anew.managers.ConnectionManager import ConnectionManager
from tensorhive.core_anew.services.Service import Service
from typing import List, Dict, Any
import time
from tensorhive.core_anew.utils.decorators.override import override


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
        elif isinstance(injected_object, ConnectionManager):
            self.connection_manager = injected_object

    def shutdown(self):
        super().shutdown()

    # TODO May want to introduce threaded workers or green threads (gevent - awesome), but need to take care of
    # accessing manager in parallel...
    @override
    def do_run(self):
        # DEBUG print(f'{self.service_name} is working...')
        for connection in self.connection_manager.connections:
            with connection:
                for monitor in self.monitors:
                    monitor.update(connection)
                    self.infrastructure_manager.update_infrastructure(
                        monitor.gathered_data)
        time.sleep(self._polling_interval)
