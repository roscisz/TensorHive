from threading import Thread
from tensorhive.core_anew.managers.ThreadedManager import ThreadedManager
from tensorhive.core_anew.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core_anew.managers.ConnectionManager import ConnectionManager
from tensorhive.core_anew.managers.ServiceManager import ServiceManager

from tensorhive.core_anew.connectors.SSHConnector import SSHConnector
from tensorhive.core_anew.services.Service import Service
from typing import List, Dict


class TensorHiveManager(ThreadedManager):
    '''
    Heart of the whole engine
    TODO should be a singleton!
    '''

    def __init__(self, services: List[Service]) -> None:
        super().__init__()
        self.infrastructure_manager = InfrastructureManager()

        # FIXME hardcoded SSHConnector
        self.connection_manager = ConnectionManager(SSHConnector())
        self.service_manager = ServiceManager(services=services,
                                              infrastructure_manager=self.infrastructure_manager,
                                              connection_manager=self.connection_manager)

    @property
    def thread_name(self):
        return f'{self.__class__.__name__} {self.name}'

    # @override
    def run(self):
        super().run()
        self.service_manager.start_all_services()

    # @override
    def start(self):
        super().start()

    # @override
    def shutdown(self):
        self.service_manager.shutdown_all_services()
        super().shutdown()
        print(f'[✔] {self.thread_name} has stopped')
