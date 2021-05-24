from typing import Dict
import json
import logging
from typing import List
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

    def node_gpu_processes(self, hostname: str) -> Dict:
        '''

        Example result:
        {
            # Most common example
            "GPU-c6d01ed6-8240-2e11-efe9-aa32794b8273": [
                {
                    "pid": 1979,
                    "command": "X",
                    "owner": "root"
                }
            ],

            # If GPU has no processes
            "GPU-abcdefg6-8240-2e11-efe9-abcdefgb8273": [],

            # If GPU does not support `nvidia-smi pmon`
            "GPU-abcdefg6-8240-2e11-efe9-abcdefgb8273": None
        }
        '''

        # Make sure we can fetch GPU data first.
        # Example reasons: node is unreachable, nvidia-smi failed
        if self.infrastructure.get(hostname, {}).get('GPU') is None:
            log.debug('There is no GPU data for host: {}'.format(hostname))
            return {}

        # Loop through each GPU on node
        node_processes = {}
        for uuid, gpu_data in self.infrastructure[hostname]['GPU'].items():
            if 'processes' in self.infrastructure[hostname]['GPU'][uuid]:
                single_gpu_processes = self.infrastructure[hostname]['GPU'][uuid]['processes']
                if single_gpu_processes is not None:
                    node_processes[uuid] = [process for process in single_gpu_processes if process['command']
                                            not in self.ignored_processes]
                else:
                    node_processes[uuid] = []
        return node_processes

    def all_nodes_with_gpu_processes(self) -> Dict[str, Dict]:
        return {node: self.node_gpu_processes(node) for node in self.infrastructure}

    # TODO: this should become obsolete when gpu_uid becomes stored in Task model
    def get_gpu_uid(self, hostname, gpu_id) -> str:
        return list(self.infrastructure[hostname]['GPU'].keys())[gpu_id]

    @property
    def ignored_processes(self):
        return [
            'Xorg',
            '/usr/lib/xorg/Xorg',
            '/usr/bin/X',
            'X',
            '-'  # nvidia-smi on TITAN X shows this for whatever reason...
        ]
