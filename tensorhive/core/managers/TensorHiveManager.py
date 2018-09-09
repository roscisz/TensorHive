from threading import Thread
from tensorhive.core.utils.Singleton import Singleton
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core.managers.ServiceManager import ServiceManager
from tensorhive.core.services.Service import Service
from typing import List, Dict
from tensorhive.core.utils.decorators.override import override
from tensorhive.config import SSH, MONITORING_SERVICE, PROTECTION_SERVICE
from tensorhive.api.APIServer import APIServer
from tensorhive.core.utils.StoppableThread import StoppableThread
from tensorhive.core.monitors.Monitor import Monitor
from tensorhive.core.monitors.GPUMonitoringBehaviour import GPUMonitoringBehaviour
from tensorhive.core.services.MonitoringService import MonitoringService
from tensorhive.core.services.ProtectionService import ProtectionService
from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.violation_handlers.MessageSendingBehaviour import MessageSendingBehaviour
import logging
log = logging.getLogger(__name__)


class TensorHiveManager(Thread, metaclass=Singleton):
    """Heart of the whole engine"""

    def __init__(self):
        super().__init__()
        self.infrastructure_manager = InfrastructureManager()
        if SSH.TEST_ON_STARTUP:
            SSHConnectionManager.test_all_connections(config=SSH.AVAILABLE_NODES)
        self.connection_manager = SSHConnectionManager(config=SSH.AVAILABLE_NODES)
        self.service_manager = None

        # Thread name
        self.name = '{}_{}'.format(self.__class__.__name__, self.name)

    @staticmethod
    def instantiate_services_from_config() -> List[Service]:
        '''Creates preconfigured instances of services based on config'''
        services = []
        if MONITORING_SERVICE.ENABLED:
            monitors = []
            if MONITORING_SERVICE.ENABLE_GPU_MONITOR:
                gpu_monitor = Monitor(GPUMonitoringBehaviour())
                monitors.append(gpu_monitor)
            # TODO Add more monitors here
            monitoring_service = MonitoringService(
                monitors=monitors, 
                interval=MONITORING_SERVICE.UPDATE_INTERVAL
            )
            services.append(monitoring_service)
        if PROTECTION_SERVICE.ENABLED:
            violation_handlers = []
            if PROTECTION_SERVICE.NOTIFY_ON_PTY:
                message_sending_handler = ProtectionHandler(behaviour=MessageSendingBehaviour())
                violation_handlers.append(message_sending_handler)
            protection_service = ProtectionService(
                handlers=violation_handlers, 
                interval=PROTECTION_SERVICE.UPDATE_INTERVAL
            )
            services.append(protection_service)
        return services

    def configure_services_from_config(self):
        services = self.instantiate_services_from_config()
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
