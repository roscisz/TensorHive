# types
from tensorhive.core_anew.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core_anew.managers.SSHConnectionManager import SSHConnectionManager

from tensorhive.core_anew.services.Service import Service
from typing import List

class ServiceManager():
    '''Encapsulates set of services'''

    def __init__(self, services: List[Service],
                 infrastructure_manager: InfrastructureManager,
                 connection_manager: SSHConnectionManager) -> None:
        self.infrastructure_manager = infrastructure_manager
        self.connection_manager = connection_manager
        self.services = services
        self.configure_all_services()

    def configure_all_services(self):
        for service in self.services:
            service.inject(self.infrastructure_manager)
            service.inject(self.connection_manager)

    def start_all_services(self):
        for service in self.services:
            service.start()

    def shutdown_all_services(self):
        for service in self.services:
            service.shutdown()
