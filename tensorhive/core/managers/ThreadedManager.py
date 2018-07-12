from threading import Thread
from tensorhive.core.monitors.Monitor import Monitor
from typing import List, Dict
from tensorhive.core.utils.decorators.override import override


class ThreadedManager(Thread):
    '''Base class with threading mechanism for managers'''

    def __init__(self):
        super().__init__()

    @property
    def thread_name(self):
        return '{class_name} {name}'.format(class_name=self.__class__.__name__, name=self.name)

    @override
    def start(self):
        super().start()

    def run(self):
        '''Overrides Thread'''
        print('[•] Starting {thread_name}'.format(thread_name=self.thread_name))

    def shutdown(self):
        print('[•] Shutting down {thread_name}'.format(thread_name=self.thread_name))
