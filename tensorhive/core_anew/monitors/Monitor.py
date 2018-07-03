from abc import ABC, abstractmethod
from typing import Dict
import spur

class Monitor(ABC):
    _id: int
    _name: str = 'Abstract Monitor'
    _gathered_data: Dict = {}
    #TODO _mode -> run all commands, specific, or single
    
    #TODO specify monitored_client type
    @abstractmethod
    def refresh(self, monitored_client_shell_session: spur.ssh.SshShell) -> None:
        pass

    #TODO discover/register methods etc.

