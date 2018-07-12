from abc import ABC, abstractmethod
from typing import Dict


class Monitor(ABC):
    '''Base class for all monitors'''

    _name: str = 'Abstract Monitor'
    _gathered_data: Dict = {}
    # TODO _mode -> run all commands, specific, or single

    @abstractmethod
    def update(self, connection) -> None:
        pass

    # TODO discover/register methods etc.
