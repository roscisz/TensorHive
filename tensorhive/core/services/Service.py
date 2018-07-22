from tensorhive.core.utils.StoppableThread import StoppableThread
from abc import abstractmethod


class Service(StoppableThread):
    '''
    Base class for all services
    '''

    def __init__(self):
        super().__init__()

    @abstractmethod
    def inject(self, injected_object):
        pass
