from tensorhive.core.monitors.MonitoringBehaviour import MonitoringBehaviour
from tensorhive.core.utils.decorators.override import override
from typing import Dict, List
from tensorhive.core.utils.NvidiaSmiParser import NvidiaSmiParser
from pssh.exceptions import Timeout, UnknownHostException, ConnectionErrorException, AuthenticationException
import logging
log = logging.getLogger(__name__)


import collections

def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]

class GPUMonitoringBehaviour(MonitoringBehaviour):
    

    @override
    def update(self, group_connection) -> Dict:
        metrics = self._query_gpu_for_metrics(group_connection)  # type: Dict
        processes = self._current_processes(group_connection)  # type: Dict
        result = self._combine_outputs(metrics, processes)  # type: Dict
        #import json
        #log.debug('METRYKI\n{}\n'.format(json.dumps(metrics, indent=4)))
        #log.debug('PROCESY\n{}\n'.format(json.dumps(processes, indent=4)))
        #dict_merge(metrics, processes)
        #metrics = self._query_gpu_for_metrics(group_connection)  # type: Dict
        #processes = self._current_processes(group_connection)  # type: Dict
        #dict_merge(processes, metrics)

        #log.debug('MERGE\n{}\n'.format(json.dumps(result, indent=4)))
        #result = metrics
        return result

    @property
    def composed_query_command(self) -> str:
        base_command = 'nvidia-smi --query-gpu='
        format_options = '--format=csv,nounits'
        available_queries = [
            'name',
            'uuid',
            'fan.speed',
            'memory.free',
            'memory.used',
            'memory.total',
            'utilization.gpu',
            'utilization.memory',
            'temperature.gpu',
            'power.draw'
        ]

        # Example: nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,utilization.memory --format=csv
        query = ','.join(available_queries)
        command = '{base_command}{query} {format_options}'.format(
            base_command=base_command,
            query=query,
            format_options=format_options)
        return command

    def _query_gpu_for_metrics(self, group_connection) -> Dict:
        '''
        Executes a query on each node within group_connection, then it 
        returns gathered information as a dictionary.
    
        Example result:
        {
            'example_host_0': {
                'GPU': {
                    '<GPU0 UUID>': { "fan_speed": 10, ... }
                    '<GPU1 UUID>': { "fan_speed": 22, ... },
                    ...
                }
            },
            ...
        }
        '''
        # stop_on_errors=False means that single host failure does not raise an exception,
        # instead simply adds them to the output.
        output = group_connection.run_command(self.composed_query_command, stop_on_errors=False)
        group_connection.join(output)

        result = {}
        for host, host_out in output.items():
            if host_out.exit_code is 0:
                # Command executed successfully
                metrics = NvidiaSmiParser.parse_query_gpu_stdout(host_out.stdout)
            else:
                # Command execution failed
                if host_out.exit_code:
                    log.error('nvidia-smi failed with {} exit code on {}'.format(host_out.exit_code, host))
                elif host_out.exception:
                    log.error('nvidia-smi raised {} on {}'.format(host_out.exception.__class__.__name__, host))
                metrics = None
            result[host] = {'GPU': metrics}
        #import json
        #log.debug('\n{}\n'.format(json.dumps(result, indent=2)))
        return result

    def _get_process_owner(self, pid: int, hostname: str, group_connection) -> str:
        '''Use single-host connection to acquire process owner'''
        # TODO Move common to SSHConnectionManager
        connection = group_connection.host_clients[hostname]
        command = 'ps --no-headers -o user {}'.format(pid)

        output = connection.run_command(command)
        channel, hostname, stdout, stderr, _ = output

        result = list(stdout)
        if not result:
            # Empty output -> Process with such pid does not exist
            return None
        # Extract owner from list ['example_owner']
        return result[0]

    def _current_processes(self, group_connection) -> Dict:
        '''
        Fetches the information about all active gpu processes using nvidia-smi pmon
        On each node, `pmon` is called for each GPU (with --id <UUID>) in order to keep consistency
        Example result:
        {
            'example_host_0': {
                'GPU': {
                    '<GPU UUID>': {
                        'processes': [
                            {
                                'gpu': 0, 
                                'pid': 1958, 
                                'type': 'G', 
                                'sm': 0, 
                                'mem': 3, 
                                'enc': 0, 
                                'dec': 0, 
                                'command': 'X'
                            },
                            ...
                        ]    
                    }
                }
            }
        }

        TERAZ ZWRACA LISTE
        '''
        command = '''
            UUIDS=$(nvidia-smi --query-gpu=uuid --format=csv,noheader)

            if [ $? -eq 0 ]; then
                echo $UUIDS | while read line; do
                    PROCESSES=$(nvidia-smi pmon --count 1 --id "$line")
                    
                    if [ $? -eq 0 ]; then
                        echo "UUID=$line"
                        echo "$PROCESSES"
                    else
                        # nvidia-smi pmon is not supported
                        exit $?
                    fi
                done 
            else
                # nvidia-smi failed
                exit $?
            fi
        '''
        output = group_connection.run_command(command, stop_on_errors=False)
        group_connection.join(output)

        result = {}
        for host, host_out in output.items():
            if host_out.exit_code is 0:
                processes = NvidiaSmiParser.parse_pmon_stdout(
                    host_out.stdout)
                # Find each process owner
                for process in processes:
                    process['owner'] = self._get_process_owner(process['pid'], host, group_connection)
            else:
                # Not Supported
                processes = None
            result[host] = processes
        #import json
        #log.debug('\n{}\n'.format(json.dumps(result, indent=2)))
        return result

    def _combine_outputs(self, metrics: Dict, processes: Dict) -> Dict:
        '''
        Merges dicts from 
        > nvidia-smi --query
        > nvidia-smi pmon

        Example result:
        {
            "example_host_0": {
                "GPU": [
                {
                    "name": "GeForce GTX 1060 6GB",
                    "uuid": "GPU-56a30ac8-fcac-f019-fb0a-1e2ffcd58a6a",
                    "fan.speed [%]": 76,
                    ...
                    "processes": [
                        {
                            "gpu": 0,
                            "pid": 1992,
                            ...
                            "command": "X",
                            "owner": "root"
                        },
                        {
                            "gpu": 0,
                            "pid": 22170,
                            ...
                            "command": "python3",
                            "owner": "143344sm"
                        }
                    ]
                }
                ]
            }
        }
        '''
        # TODO May want to refactor in the future
        for hostname, gpu_processes_on_node in processes.items():
            # Loop thorugh each item on GPU list and create a new key with default value
            # node_gpus = metrics[hostname]['GPU']  # type: List[Dict]
            # for uuid, data in node_gpus.items():
            #     metrics[hostname]['GPU'][uuid]['processes'] = []

            # Loop through all processes and assign them into corresponding places in a list
            # type: List[Dict]
            


            # if gpu_processes_on_node is None:
            #     for uuid, data in metrics[hostname]['GPU'].items():
            #         metrics[hostname]['GPU'][uuid]['processes'] = None
            
            # Initialize
            if gpu_processes_on_node is None:
                for uuid, _ in metrics[hostname]['GPU'].items():
                    metrics[hostname]['GPU'][uuid]['processes'] = None
            else:
                for uuid, _ in metrics[hostname]['GPU'].items():
                    metrics[hostname]['GPU'][uuid]['processes'] = []

                for process in gpu_processes_on_node:
                    uuid = process.pop('uuid') 
                    metrics[hostname]['GPU'][uuid]['processes'].append(process)
        return metrics
