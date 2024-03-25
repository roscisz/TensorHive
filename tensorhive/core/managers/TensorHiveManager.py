from threading import Thread
from tensorhive.core.utils.Singleton import Singleton
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core.managers.ServiceManager import ServiceManager
from tensorhive.core.services.Service import Service
from typing import List, Dict
from tensorhive.core.utils.decorators import override
from tensorhive.config import (SSH, MONITORING_SERVICE, PROTECTION_SERVICE, USAGE_LOGGING_SERVICE,
                               JOB_SCHEDULING_SERVICE)
from tensorhive.api.APIServer import APIServer
from tensorhive.core.utils.StoppableThread import StoppableThread
from tensorhive.core.utils.exceptions import ConfigurationException
from tensorhive.core.monitors.Monitor import Monitor
from tensorhive.core.monitors.GPUMonitor import GPUMonitor
from tensorhive.core.monitors.CPUMonitor import CPUMonitor
from tensorhive.core.services.MonitoringService import MonitoringService
from tensorhive.core.services.ProtectionService import ProtectionService
from tensorhive.core.services.UsageLoggingService import UsageLoggingService
from tensorhive.core.services.JobSchedulingService import JobSchedulingService
from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.violation_handlers.MessageSendingBehaviour import MessageSendingBehaviour
from tensorhive.core.violation_handlers.EmailSendingBehaviour import EmailSendingBehaviour
from tensorhive.core.violation_handlers.UserProcessKillingBehaviour import UserProcessKillingBehaviour
from tensorhive.core.violation_handlers.SudoProcessKillingBehaviour import SudoProcessKillingBehaviour
from tensorhive.core.scheduling import GreedyScheduler
from tensorhive.core import ssh
from pathlib import PosixPath
import logging
log = logging.getLogger(__name__)


class TensorHiveManager(metaclass=Singleton):
    """Heart of the whole engine"""

    def __init__(self):
        super().__init__()
        self.infrastructure_manager = InfrastructureManager(SSH.AVAILABLE_NODES)

        self.dedicated_ssh_key_path = PosixPath(SSH.KEY_FILE).expanduser()
        self.dedicated_ssh_key = ssh.init_ssh_key(self.dedicated_ssh_key_path)

        if not SSH.AVAILABLE_NODES:
            log.error('[!] Empty ssh configuration. Please check {}'.format(SSH.HOSTS_CONFIG_FILE))
            raise ConfigurationException

        manager_ssh_key_path = SSH.KEY_FILE
        if SSH.TEST_ON_STARTUP:
            manager_ssh_key_path = self.test_ssh()

        self.connection_manager = SSHConnectionManager(config=SSH.AVAILABLE_NODES, ssh_key_path=manager_ssh_key_path)
        self.service_manager = None

    @staticmethod
    def test_ssh():
        """
        Test SSH connectivity using dedicated key. If some nodes are failing, try default system-wide key.
        :return: Key filename or None (meaning system-wide key) for the best performing key.
        """
        ret = SSH.KEY_FILE

        failed_dedicated = SSHConnectionManager.test_all_connections(config=SSH.AVAILABLE_NODES, key_path=SSH.KEY_FILE)

        if failed_dedicated > 0:
            failed_system = SSHConnectionManager.test_all_connections(config=SSH.AVAILABLE_NODES)
            if failed_system < failed_dedicated:
                log.info('[⚙] TensorHive will be using default system keys for monitoring SSH connections')
                ret = None

        return ret

    @staticmethod
    def instantiate_services_from_config() -> List[Service]:
        '''Creates preconfigured instances of services based on config'''
        services = []  # type: List[Service]
        if MONITORING_SERVICE.ENABLED:
            monitors = [CPUMonitor()]  # type: List[Monitor]
            if MONITORING_SERVICE.ENABLE_GPU_MONITOR:
                monitors.append(GPUMonitor())
            # TODO Add more monitors here
            monitoring_service = MonitoringService(monitors=monitors, interval=MONITORING_SERVICE.UPDATE_INTERVAL)
            services.append(monitoring_service)
        if JOB_SCHEDULING_SERVICE.ENABLED:
            job_scheduling_service = JobSchedulingService(
                interval=JOB_SCHEDULING_SERVICE.UPDATE_INTERVAL,
                stop_attempts_after=JOB_SCHEDULING_SERVICE.STOP_TERMINATION_ATTEMPTS_AFTER)
            # TODO: scheduler configuration when more schedulers are available
            job_scheduling_service.inject(GreedyScheduler())
            services.append(job_scheduling_service)
        if PROTECTION_SERVICE.LEVEL:
            violation_handlers = []
            if PROTECTION_SERVICE.NOTIFY_ON_PTY:
                message_sending_handler = ProtectionHandler(behaviour=MessageSendingBehaviour())
                violation_handlers.append(message_sending_handler)
            if PROTECTION_SERVICE.NOTIFY_VIA_EMAIL:
                email_sending_handler = ProtectionHandler(behaviour=EmailSendingBehaviour())
                violation_handlers.append(email_sending_handler)
            if PROTECTION_SERVICE.KILL_PROCESSES:
                if PROTECTION_SERVICE.KILL_PROCESSES > 1:
                    process_killing_handler = ProtectionHandler(behaviour=SudoProcessKillingBehaviour())
                else:
                    process_killing_handler = ProtectionHandler(behaviour=UserProcessKillingBehaviour())
                violation_handlers.append(process_killing_handler)
            protection_service = ProtectionService(
                handlers=violation_handlers, interval=PROTECTION_SERVICE.UPDATE_INTERVAL,
                strict_reservations=PROTECTION_SERVICE.LEVEL > 1)
            services.append(protection_service)
        if USAGE_LOGGING_SERVICE.ENABLED:
            usage_logging_service = UsageLoggingService(interval=USAGE_LOGGING_SERVICE.UPDATE_INTERVAL)
            services.append(usage_logging_service)
        return services

    def configure_services_from_config(self):
        services = self.instantiate_services_from_config()
        self.service_manager = ServiceManager(
            services=services,
            infrastructure_manager=self.infrastructure_manager,
            connection_manager=self.connection_manager)

    def init(self):
        log.info('[⚙] Initializing services {}...'.format(self.__class__.__name__))
        self.service_manager.start_all_services()

    def shutdown(self):
        log.info('[⚙] Shutting down all services...')
        self.service_manager.shutdown_all_services()
