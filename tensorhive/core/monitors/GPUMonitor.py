from tensorhive.core.monitors.Monitor import Monitor
from tensorhive.core.utils.decorators.override import override
from typing import Dict, List
from tensorhive.core.utils.NvidiaSmiParser import NvidiaSmiParser

# TODO Revert full type annotations for variables as they were (python 3.5 => python 3.6)


class GPUMonitor(Monitor):
    base_command = 'nvidia-smi --query-gpu='
    format_options = '--format=csv'  # ,nounits
    _available_commands = [
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
        assert (lines and len(lines) >
                1), 'Cannot parse result: {}'.format(lines)
        header = lines[0]  # type: str
        parameter_keys = header.split(', ')  # type: List[str]
        results_for_gpus = lines[1:]  # type: List[str]

        gpus_info = []  # type: List[Dict]
        for single_gpu_result_line in results_for_gpus:
            parameter_values = single_gpu_result_line.split(
                ', ')  # type: List[str]
            gpu_info = dict(
                zip(parameter_keys, parameter_values))
            gpus_info.append(gpu_info)
        return gpus_info

    @override
    def update(self, connection_group):
        query = ','.join(self.available_commands)  # type: str
        command = '{base_command}{query} {format_options}'.format(
            base_command=self.base_command, query=query, format_options=self.format_options)  # type: str
        output = connection_group.run_command(command)

        connection_group.join(output)

        for host, host_out in output.items():
            if host_out.exit_code is 0:
                gpus_info = NvidiaSmiParser.gpus_info_from_stdout(
                    host_out.stdout)  # type: Dict[str, str]
                self.gathered_data[host] = gpus_info
            else:
                self.gathered_data[host] = []
