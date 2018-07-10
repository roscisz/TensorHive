from threading import Thread
from abc import abstractmethod

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