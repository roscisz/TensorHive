from typing import Dict
import json


class InfrastructureManager():
    '''
    Holds the state/representation of discovered/known infrastruture with metrics
    '''
    _infrastructure = {}

    @property
    def infrastructure(self) -> Dict:
        return self._infrastructure

    def update_infrastructure(self, new_value: Dict):
        self._infrastructure = new_value
        # FIXME Remove, debug only
        print(json.dumps(self._infrastructure, indent=2))
