from abc import ABC, abstractmethod


class MonitoringBehaviour(ABC):
    '''
    Interface that needs to be implemented by concrete classes
    (Strategy pattern)
    '''

    @abstractmethod
    def update(self, connection) -> None:
        pass
