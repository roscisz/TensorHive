from threading import Thread
from abc import abstractmethod
from tensorhive.core.utils.decorators import override
import logging
log = logging.getLogger(__name__)


class StoppableThread(Thread):
    def __init__(self):
        super().__init__()
        self.stop = False
        self.name = '{}_{}'.format(self.__class__.__name__, self.name)

    @override
    def run(self):
        self.before_execution()
        while not self.stop:
            self.do_run()

    @abstractmethod
    def do_run(self):
        '''Override with a cyclic task'''
        pass

    def shutdown(self):
        self.stop = True
        self.after_execution()

    def before_execution(self):
        log.info('[⚙] Starting {}'.format(self.name))

    def after_execution(self):
        log.info('[✔] Stopped {}'.format(self.name))
