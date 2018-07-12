from typing import Dict
import json
class InfrastructureManager():
    '''
    Holds the state/representation of discovered/known infrastruture
    '''
    _infrastructure: Dict = {}

    #TODO Add observer design pattern. 
    # Observator must be responsible for updating database when infrastructure changes

    @property
    def infrastructure(self) -> Dict:
        #FIXME Only for testing purposes
        
        return self._infrastructure

    def update_infrastructure(self, new_value: Dict):
        self._infrastructure = new_value
        #FIXME Remove, debug only
        print(json.dumps(self._infrastructure, indent=2))


