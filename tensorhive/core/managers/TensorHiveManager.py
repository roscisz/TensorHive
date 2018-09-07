from threading import Thread
from tensorhive.core.utils.Singleton import Singleton
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core.managers.ServiceManager import ServiceManager
from tensorhive.core.services.Service import Service
from typing import List, Dict
from tensorhive.core.utils.decorators.override import override
from tensorhive.config import SSH_CONFIG, API_CONFIG
from tensorhive.api.APIServer import APIServer
from tensorhive.core.utils.StoppableThread import StoppableThread
import logging
log = logging.getLogger(__name__)


class TensorHiveManager(Thread, metaclass=Singleton):
    """Heart of the whole engine"""

    def __init__(self):
        super().__init__()
        self.infrastructure_manager = InfrastructureManager()
        if SSH_CONFIG.TEST_CONNECTIONS_ON_STARTUP:
            SSHConnectionManager.test_all_connections(config=SSH_CONFIG.AVAILABLE_NODES)
        self.connection_manager = SSHConnectionManager(config=SSH_CONFIG.AVAILABLE_NODES)
        self.service_manager = None

        # Thread name
        self.name = '{}_{}'.format(self.__class__.__name__, self.name)

    def configure_services(self, services: List[Service]):
        self.service_manager = ServiceManager(services=services,
                                              infrastructure_manager=self.infrastructure_manager,
                                              connection_manager=self.connection_manager)

    @override
    def run(self):
        log.info('[•] Starting {}'.format(self.name))
        self.service_manager.start_all_services()

    @override
    def shutdown(self):
        self.service_manager.shutdown_all_services()
        log.info('[✔] Stopped {}'.format(self.name))
