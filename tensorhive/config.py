from typing import Any, Dict, Union, ClassVar

# TODO Add reading command-line arguments with argparse e.g. tensorhive --host localhost --port 1234
class BaseConfig():
    '''Contains ALL configuration constants'''
    StringOrInt = Union[str, int]
    CONFIG: Dict[str, StringOrInt]

    def __init__(self) -> None:
        # Put all keys with default values here...
        self.CONFIG = {
            'TH__SERVER_HOSTNAME': 'localhost',
            'TH__SERVER_PORT': 31333,
            'TH__SLEEP_IN_S': 5

        }

    def __repr__(self):
        return self.CONFIG
    

class DevelopmentConfig(BaseConfig):
    '''Default config, can overwrite BaseConfig'''
    def __init__(self) -> None:
        super().__init__()

        # Override here...
        self.CONFIG['TH__SERVER_PORT'] = 31333
        self.CONFIG['TH__SLEEP_IN_S'] = 1

    
class ProductionConfig(BaseConfig):
    '''Production use only, can overwrite BaseConfig'''
    pass

# Object to be imported by application modules
CONFIG = DevelopmentConfig().CONFIG


