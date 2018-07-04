from tensorhive.core_anew.connectors.SSHConnector import SSHConnector
from tensorhive.core_anew.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core_anew.managers.ConnectionManager import ConnectionManager
from tensorhive.core_anew.services.Service import Service
from typing import List, Dict, Any


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
    _polling_interval: float = 3.0

    def __init__(self, monitors):
        super().__init__()
        self.monitors = monitors

    # @override
    def start(self):
        super().start()

    # @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self.infrastructure_manager = injected_object
        elif isinstance(injected_object, ConnectionManager):
            self.connections = injected_object.connections

    def shutdown(self):
        super().shutdown()

    # @override
    # TODO May want to introduce threaded workers, but need to take care of
    # accessing manager in parallel mode...
    def do_run(self):
        print(f'{self.service_name} is working...')
        for connection in self.connections:
            with connection:
                for monitor in self.monitors:
                    monitor.update(connection)
                    self.infrastructure_manager.update_infrastructure(
                        monitor.gathered_data)
        time.sleep(self._polling_interval)
