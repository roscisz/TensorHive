from tensorhive.core_anew.utils.StoppableThread import StoppableThread
from abc import abstractmethod

class Service(StoppableThread):
    '''
    Base class for all services
    '''
    
    def __init__(self):
        super().__init__()

    @property
    def service_name(self):
        return f'{self.__class__.__name__} {self.name}'

    def start(self):
        '''Overrides Thread'''
        print(f' └─ Starting {self.service_name}')
        
    #@inherited
    @abstractmethod
    def do_run(self):
        pass
    
    @abstractmethod
    def inject(self, injected_object):
        pass

    def shutdown(self):
        print(f' └─ Shutting down {self.service_name}')