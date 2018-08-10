from tensorhive.core.monitors.MonitoringBehaviour import MonitoringBehaviour
from tensorhive.core.utils.decorators.override import override
from typing import Dict, List
from tensorhive.core.utils.NvidiaSmiParser import NvidiaSmiParser
from pssh.exceptions import Timeout, UnknownHostException, ConnectionErrorException, AuthenticationException


class GPUMonitoringBehaviour(MonitoringBehaviour):
    _base_command = 'nvidia-smi --query-gpu='
    _format_options = '--format=csv,nounits'
    _available_queries = [
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

    @override
    def update(self, group_connection) -> Dict:
        metrics = self._current_metrics(group_connection)  # type: Dict
        processes = self._current_processes(group_connection)  # type: Dict
        result = self._combine_outputs(metrics, processes)  # type: Dict
        return result

    @property
    def available_queries(self) -> List:
        return self._available_queries

    def _current_metrics(self, group_connection) -> Dict:
        '''
        Merges all commands into a single nvidia-smi query 
        and executes them on all hosts within connection group
        '''

        # Example: nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,utilization.memory --format=csv
        query = ','.join(self.available_queries)
        command = '{base_command}{query} {format_options}'.format(
            base_command=self._base_command, query=query, format_options=self._format_options
        )  # type: str

        # stop_on_errors=False means that single host failure does not raise an exception,
        # instead simply adds them to the output.
        output = group_connection.run_command(command, stop_on_errors=False)
        group_connection.join(output)

        result = {}
        for host, host_out in output.items():
            if host_out.exit_code is 0:
                '''Command executed successfully'''
                metrics = NvidiaSmiParser.gpus_info_from_stdout(
                    host_out.stdout)
            else:
                '''Command execution failed'''
                if host_out.exit_code:
                    message = {'exit_code': host_out.exit_code}
                elif host_out.exception:
                    message = {
                        'exception': host_out.exception.__class__.__name__}
                else:
                    message = 'Unknown failure'
                # May want to assign None
                metrics = message
            result[host] = {'GPU': metrics}
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

        Example result:
        {
            'example_host_0': {
                'GPU': {
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
                        }
                    ]    
                }
            }
        }
        '''
        command = 'nvidia-smi pmon --count 1'
        output = group_connection.run_command(command, stop_on_errors=False)
        group_connection.join(output)

        result = {}
        for host, host_out in output.items():
            if host_out.exit_code is 0:
                processes = NvidiaSmiParser.parse_pmon(host_out.stdout)

                # Find each process owner
                for process in processes:
                    process['owner'] = self._get_process_owner(
                        process['pid'], host, group_connection)
            else:
                # Not Supported
                processes = []
            result[host] = {'GPU': {'processes': processes}}
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
        for hostname, _ in processes.items():
            gpu_processes_on_host = processes[hostname]['GPU']['processes']
                
            for gpu_device_idx, gpu_device in enumerate(metrics[hostname]['GPU']):
                metrics[hostname]['GPU'][gpu_device_idx]['processes'] = []    
            
            for process in gpu_processes_on_host:
                # Put 'process' element at particular index in array
                # FIXME Replace with pythonic code :) Author's intentions are unreadable
                metrics[hostname]['GPU'][process['gpu']]['processes'].append(process)
        return metrics
