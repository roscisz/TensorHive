from threading import Thread
from tensorhive.core.utils.Singleton import Singleton
from tensorhive.core.managers.ThreadedManager import ThreadedManager
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core.managers.ServiceManager import ServiceManager


from tensorhive.core.services.Service import Service
from typing import List, Dict

# FIXME Remove colorama dependency from setup.py
from colorama import Fore, Back, Style
from tensorhive.core.utils.decorators.override import override
from tensorhive.config import CONFIG, SSH_CONFIG, API_CONFIG
from tensorhive.api.APIServer import APIServer
import logging
log = logging.getLogger(__name__)


class TensorHiveManager(ThreadedManager, metaclass=Singleton):
    """Heart of the whole engine"""

    def __init__(self):
        super().__init__()
        self.infrastructure_manager = InfrastructureManager()
        log.warning('You need to replace hostnames and usernames to your own in tensorhive/config.py')
        self.connection_manager = SSHConnectionManager(
            config=SSH_CONFIG.AVAILABLE_NODES)
        self.service_manager = None

    def configure_services(self, services: List[Service]):
        self.service_manager = ServiceManager(services=services,
                                              infrastructure_manager=self.infrastructure_manager,
                                              connection_manager=self.connection_manager)

    @property
    def thread_name(self):
        return '{class_name} {name}'.format(class_name=self.__class__.__name__, name=self.name)

    @override
    def run(self):
        super().run()
        self.service_manager.start_all_services()

    @override
    def start(self):
        super().start()

    @override
    def shutdown(self):
        self.service_manager.shutdown_all_services()
        super().shutdown()
        print('[✔] {thread_name} has stopped'.format(
            thread_name=self.thread_name))
