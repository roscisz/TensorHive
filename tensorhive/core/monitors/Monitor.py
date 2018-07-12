from abc import ABC, abstractmethod
from typing import Dict


class Monitor(ABC):
    '''Base class for all monitors'''

    _name = 'Abstract Monitor'
    _gathered_data = {}

    @abstractmethod
    def update(self, connection) -> None:
        pass

    # TODO discover/register methods etc.
