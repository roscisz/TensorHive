from tensorhive.core.utils.StoppableThread import StoppableThread
from abc import abstractmethod

class Service(StoppableThread):
    '''
    Base class for all services
    '''
    
    def __init__(self):
        super().__init__()

    @property
    def service_name(self):
        return '{class_name} {name}'.format(class_name=self.__class__.__name__,name=self.name)

    def start(self):
        '''Overrides Thread'''
        print(' └─ Starting {service_name}'.format(service_name=self.service_name))
        super().run()
        
    #@inherited
    @abstractmethod
    def do_run(self):
        pass
    
    @abstractmethod
    def inject(self, injected_object):
        pass

    def shutdown(self):
        super().shutdown()
        print(' └─ Shutting down {service_name}'.format(service_name=self.service_name))