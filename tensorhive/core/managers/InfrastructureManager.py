from typing import Dict
import json
import logging
log = logging.getLogger(__name__)


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
        log.debug('\n{}\n'.format(json.dumps(self._infrastructure, indent=4)))
