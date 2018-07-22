from threading import Thread
from abc import abstractmethod
import logging
log = logging.getLogger(__name__)

class StoppableThread(Thread):
    def __init__(self):
        super().__init__()
        self.stop = False

    def shutdown(self):
        self.stop = True

    def run(self):
        while not self.stop:
            self.do_run()
        self.finalize()

    @abstractmethod
    def do_run(self):
        pass

    @abstractmethod
    def finalize(self):
        pass

    def shutdown(self):
        self.stop = True
        self.after_execution()

    def before_execution(self):
        log.info('[•] Starting {}'.format(self.name))

    def after_execution(self):
        log.info('[✔] Stopped {}'.format(self.name))
