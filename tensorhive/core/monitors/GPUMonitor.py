from tensorhive.core.monitors.Monitor import Monitor
from tensorhive.core.utils.decorators import override
from typing import Dict, List
from tensorhive.core.utils.NvidiaSmiParser import NvidiaSmiParser
from pssh.exceptions import Timeout, UnknownHostException, ConnectionErrorException, AuthenticationException
import logging
log = logging.getLogger(__name__)


class GPUMonitor(Monitor):
    '''Responsible for fetching data about installed GPUs within configured network'''

    @override
    def update(self, group_connection, infrastructure_manager):
        self._update_gpu_metrics(group_connection, infrastructure_manager)
        processes = self._current_processes(group_connection, infrastructure_manager)  # type: Dict
        self._update_processes(infrastructure_manager, processes)

    @property
    def composed_query_command(self) -> str:
        '''
        Builds a query command for nvidia-smi that can be executed on each node

        Example result:
        nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,utilization.memory --format=csv
        '''
        base_command = 'nvidia-smi --query-gpu='
        format_options = '--format=csv,nounits'
        available_queries = [
            'name',
            'uuid',
            'index',
            'fan.speed',
            'memory.free',
            'memory.used',
            'memory.total',
            'utilization.gpu',
            'utilization.memory',
            'temperature.gpu',
            'power.draw'
        ]

        query = ','.join(available_queries)
        command = '{base_command}{query} {format_options}'.format(
            base_command=base_command,
            query=query,
            format_options=format_options)
        return command

    def _update_gpu_metrics(self, group_connection, infrastructure_manager):
        '''
        Executes a query on each node within group_connection, then
        it returns gathered information as a dictionary.

        Example result:
        {
            'example_host_0': {
                'GPU': {
                    '<GPU0 UUID>': {
                        'name': 'GeForce GTX 660',
                        'index': 0,
                        'metrics': { "fan_speed": 10, ... }
                    }
                    '<GPU1 UUID>': {
                        'name': 'GeForce GTX 1060'
                        'index': 1,
                        'metrics': { "fan_speed": 22, ... },
                    },
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

        for host, host_out in output.items():
            if host_out.exit_code == 0:
                # Command executed successfully
                metrics = NvidiaSmiParser.parse_query_gpu_stdout(host_out.stdout)
            else:
                # Command execution failed
                if host_out.exit_code:
                    log.error('nvidia-smi failed with {} exit code on {}'.format(host_out.exit_code, host))
                elif host_out.exception:
                    log.error('nvidia-smi raised {} on {}'.format(host_out.exception.__class__.__name__, host))
                metrics = None

            infrastructure_manager.infrastructure[host]['GPU'] = metrics

    def _get_process_owner(self, pid: int, hostname: str, connection) -> str:
        '''Use single-host connection to acquire process owner using `ps`'''
        command = 'ps --no-headers -o user {}'.format(pid)
        connection = connection.host_clients[hostname]

        output = connection.run_command(command)
        _, hostname, stdout, stderr, _ = output

        result = list(stdout)
        if not result:
            # Empty output -> Process with such pid does not exist
            return None
        # Unpack owner from the list (e.g. ['example_owner'])
        return result[0]

    @property
    def get_gpu_processes_command(self):
        '''
        Returns short bash script that can be executed on each node.
        Script tries to execute nvidia-smi pmon for each UUID separately.

        Explanation for this is that GPUs' indexes are not fixed in time,
        hence UUID parameter.

        When executed, gives output, like:
            UUID=GPU-c6d01ed6-8240-2e11-efe9-1111111111111
            # gpu        pid  type    sm   mem   enc   dec   command
            # Idx          #   C/G     %     %     %     %   name
                0       1979     G     0     3     0     0   X
                1       1234     G     0    90     0     0   python
                1       4567     G     0    89     0     0   python
            UUID=GPU-c6d01ed6-8240-2e11-efe9-2222222222222
            # gpu        pid  type    sm   mem   enc   dec   command
            # Idx          #   C/G     %     %     %     %   name
                0       1979     G     0     3     0     0   X
                1       1234     G     0    90     0     0   python
                1       4567     G     0    89     0     0   python
            UUID=GPU-7fcc76c8-ac23-0ead-83ce-3f6f3d831d8a
            [PMON NOT SUPPORTED]
        '''
        return '''
            # Get a list of UUIDs of each installed GPU in the system
            UUIDS=$(nvidia-smi --query-gpu=uuid --format=csv,noheader)

            # Check exit code
            if [ $? -eq 0 ]; then
                # Success (nvidia-smi is installed)
                # Read UUIDs, 1 line = 1 UUID
                echo "$UUIDS" | while read line; do
                    echo "UUID=$line"

                    # Fetch a list of processes on this GPU
                    PROCESSES=$(nvidia-smi pmon --count 1 --id "$line")

                    if [ $? -eq 0 ]; then
                        echo "$PROCESSES"
                    else
                        echo "[PMON NOT SUPPORTED]"
                    fi
                done
            else
                # nvidia-smi failed
                exit $?
            fi
        '''

    def _current_processes(self, group_connection, infrastructure_manager) -> Dict:
        '''
        Fetches the information about all active gpu processes using nvidia-smi pmon

        Example result:
        {
            "pmon_capable_hostname": [
                {
                    "uuid": "GPU-c6d01ed6-8240-2e11-efe9-aa32794b8273",
                    "pid": 1979,
                    "command": "X",
                    "owner": "root"
                }
            ],
            "pmon_not_supported_hostname": null
        }
        '''
        output = group_connection.run_command(self.get_gpu_processes_command, stop_on_errors=False)
        group_connection.join(output)

        result = {}
        for host, host_out in output.items():
            if host_out.exit_code == 0:
                processes = NvidiaSmiParser.parse_pmon_stdout(host_out.stdout)
                # Find process owner for each process
                for process in processes:
                    process['owner'] = self._get_process_owner(process['pid'], host, group_connection)
            else:
                # Possible reasons:
                # - nvidia-smi not installed
                # - could not connect to host
                processes = None
            result[host] = processes
        return result

    def _update_processes(self, infrastructure_manager, processes: Dict):
        '''
        Updates processes for the appropriate GPU records in infrastructure manager

        Example result:
        {
            "example_host_0": {
                "GPU": {
                    "GPU-c6d01ed6-8240-2e11-efe9-aa32794b8273": {
                        "name": "GeForce GTX 1060 6GB",
                        "index": 0,
                        "metrics": {
                            "fan_speed": {
                                "value": 25,
                                "unit": "%"
                            },
                            "temp": 40,
                            ...
                        },
                        "processes": [
                            {
                                "pid": 1979,
                                "command": "X",
                                "owner": "root"
                            }
                        ]
                    }
                }
            },
        }
        '''
        for hostname, gpu_processes_on_node in processes.items():
            if infrastructure_manager.infrastructure[hostname].get('GPU') is None:
                # Can't access any GPU right now, e.g. could not connect to host or nvidia-smi failure
                continue

            # Introduce new key - 'processes' with default value
            for uuid, _ in infrastructure_manager.infrastructure[hostname]['GPU'].items():
                infrastructure_manager.infrastructure[hostname]['GPU'][uuid]['processes'] = None

            # Unpack every known process and move to the corresponding GPU
            for process in gpu_processes_on_node:
                uuid = process.pop('uuid')

                # Replace default value with an empty list, because we have a new process to append
                if infrastructure_manager.infrastructure[hostname]['GPU'][uuid]['processes'] is None:
                    infrastructure_manager.infrastructure[hostname]['GPU'][uuid]['processes'] = []
                infrastructure_manager.infrastructure[hostname]['GPU'][uuid]['processes'].append(process)
