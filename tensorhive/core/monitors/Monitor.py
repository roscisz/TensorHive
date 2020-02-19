from abc import ABC, abstractmethod
from typing import Dict


class Monitor(ABC):
    '''
    Interface that needs to be implemented by concrete classes
    (Strategy pattern)
    '''

    @abstractmethod
    def update(self, connection, infrastructure_manager) -> None:
        pass
