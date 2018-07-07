from tensorhive.core_anew.monitors.Monitor import Monitor
from tensorhive.core_anew.utils.decorators.override import override
from typing import Dict, List
import fabric
import invoke


class GPUMonitor(Monitor):
    base_command: str = 'nvidia-smi --query-gpu='
    format_options: str = '--format=csv' #,nounits
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
            list_of_stdout_lines = list(host_out.stdout)

            if host_out.exit_code is 0:
                gpus_info = self._parse_lines(list_of_stdout_lines)
                self.gathered_data[host] = gpus_info
            else:
                self.gathered_data[host] = []
            # self.gathered_data[command] = 
            



            # # TODO Parse this big response, split into dict
            # self.gathered_data[host] = {
            #     command: {
            #         'result': list_of_stdout_lines,
            #         'exit_code': host_out.exit_code
            #     }
            # }

    

    @override
    def OLD_update(self, connection_group) -> None:
        '''
        Attaches to given shell session,
        updates info about monitored resource,
        replaces old data (old state) with current
        '''
        # TODO Catch all errors
        # TODO Organize dict structure (see how fabric handles this)
        # FIXME Too many simplifications
        # DEBUG print(f'Benchmark with {len(connection_group)} nodes on {type(connection_group)}')
        #def run(command): return connection_group.run(command, hide=True)
        #with Pool(processes=4) as pool:
        #    results = pool.map(run, self.available_commands.items(), 2)

        for command_key, command_str in self.available_commands.items():
            try:
                results = connection_group.run(command_str, hide=True)
            except fabric.exceptions.GroupException as e:
                results = e.result
            finally:
                for connection, result in results.items():
                    if isinstance(result, fabric.runners.Result):
                        self.gathered_data[connection.host] = {
                            command_key: {
                                'result': result.stdout.strip('\n'),
                                'exit_code': result.exited
                            }
                        }
                    elif isinstance(result, invoke.exceptions.UnexpectedExit):
                        self.gathered_data[connection.host] = {
                            command_key: {
                                'result': 'Execution error',
                                'exit_code': result.result.exited
                            }
                        }


