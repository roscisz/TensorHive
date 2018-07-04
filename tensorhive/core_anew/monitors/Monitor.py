from abc import ABC, abstractmethod
from typing import Dict
import spur


class Monitor(ABC):
    '''Base class for all monitors'''

    _name: str = 'Abstract Monitor'
    _gathered_data: Dict = {}
    # TODO _mode -> run all commands, specific, or single

    @abstractmethod
    def refresh(self, monitored_client_shell_session: spur.ssh.SshShell) -> None:
        pass

    # TODO discover/register methods etc.
