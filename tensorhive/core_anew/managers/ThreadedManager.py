from threading import Thread
from tensorhive.core_anew.monitors.Monitor import Monitor
from typing import List, Dict
from tensorhive.core_anew.utils.decorators.override import override


class ThreadedManager(Thread):
    '''Base class with threading mechanism for managers'''

    def __init__(self):
        super().__init__()

    @property
    def thread_name(self):
        return f'{self.__class__.__name__} {self.name}'

    @override
    def start(self):
        super().start()

    def run(self):
        '''Overrides Thread'''
        print(f'[•] Starting {self.thread_name}')

    def shutdown(self):
        print(f'[•] Shutting down {self.thread_name}')
