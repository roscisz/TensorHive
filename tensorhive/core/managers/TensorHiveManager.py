from threading import Thread
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


class TensorHiveManager(ThreadedManager):
    # TODO should be a singleton!
    '''Heart of the whole engine'''

    def __init__(self, services: List[Service]):
        super().__init__()
        self.infrastructure_manager = InfrastructureManager()

        # FIXME hardcoded SSHConnector
        print(f'{Back.RED}WARNING! You need to replace hostname and username in tensorhive/core/managers/TensorHiveManager.py{Style.RESET_ALL}')

        self.connection_manager = SSHConnectionManager(
            SSH_CONFIG.AVAILABLE_NODES)
        self.service_manager = ServiceManager(services=services,
                                              infrastructure_manager=self.infrastructure_manager,
                                              connection_manager=self.connection_manager)

    @property
    def thread_name(self):
        return f'{self.__class__.__name__} {self.name}'

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
        print(f'[✔] {self.thread_name} has stopped')
