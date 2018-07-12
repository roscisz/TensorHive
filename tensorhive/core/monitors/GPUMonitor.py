from tensorhive.core.monitors.Monitor import Monitor
from tensorhive.core.utils.decorators.override import override
from typing import Dict, List
from tensorhive.core.utils.NvidiaSmiParser import NvidiaSmiParser


class GPUMonitor(Monitor):
    base_command: str = 'nvidia-smi --query-gpu='
    format_options: str = '--format=csv'  # ,nounits
    _available_commands: List = [
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

    @property
    def available_commands(self) -> List:
        return self._available_commands

    @property
    def name(self) -> str:
        return 'GPU'

    @property
    def gathered_data(self) -> Dict:
        '''Getter for the protected, inherited variable'''
        return self._gathered_data

    @gathered_data.setter
    def gathered_data(self, new_value) -> None:
        '''Setter for the protected, inherited variable'''
        self._gathered_data = new_value

    # TODO Make separate class for it
    def _parse_lines(self, lines: List) -> Dict:
        '''Assumes that header is present'''
        assert (lines and len(lines) > 1), f'Cannot parse result: {lines}'
        header: str = lines[0]
        parameter_keys: List[str] = header.split(', ')
        results_for_gpus: List[str] = lines[1:]

        gpus_info = []
        for single_gpu_result_line in results_for_gpus:
            parameter_values: List[str] = single_gpu_result_line.split(', ')
            gpu_info = dict(zip(parameter_keys, parameter_values))
            gpus_info.append(gpu_info)
        return gpus_info

    @override
    def update(self, connection_group):
        query = ','.join(self.available_commands)
        command = f'{self.base_command}{query} {self.format_options}'
        output = connection_group.run_command(command)

        connection_group.join(output)

        for host, host_out in output.items():
            if host_out.exit_code is 0:
                gpus_info = NvidiaSmiParser.gpus_info_from_stdout(
                    host_out.stdout)
                self.gathered_data[host] = gpus_info
            else:
                self.gathered_data[host] = []
