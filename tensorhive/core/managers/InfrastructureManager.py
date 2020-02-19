from typing import Dict
import json
import logging
log = logging.getLogger(__name__)


class InfrastructureManager():
    '''
    Holds the state/representation of discovered/known infrastruture with metrics
    '''

    def __init__(self, available_nodes):
        self._infrastructure = {}  # type: Dict
        for node in available_nodes.keys():
            self._infrastructure[node] = {}  # type: Dict

    @property
    def infrastructure(self) -> Dict:
        return self._infrastructure
