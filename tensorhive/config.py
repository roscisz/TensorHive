# TODO Add reading command-line arguments with argparse e.g. tensorhive --host localhost --port 1234

class BaseConfig:
    '''Contains ALL configuration constants'''
    def __init__(self):
        # Put all keys with default values here...
        self.CONFIG = {
            'THManager': {
                'server': {
                    'hostname': 'localhost',
                    'port': 12345
                }
            }
        }

    def __repr__(self):
        return self.CONFIG
    
    def get_config(self):
        return self.CONFIG

class DevelopmentConfig(BaseConfig):
    '''Default config, can overwrite BaseConfig'''
    def __init__(self):
        super().__init__()

        # Override here...
        self.CONFIG['THManager']['server']['port'] = 31333

    
class ProductionConfig(BaseConfig):
    '''Production use only, can overwrite BaseConfig'''
    pass

# Object to be imported by application modules
CONFIG = DevelopmentConfig().get_config()


