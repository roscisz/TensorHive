from tensorhive.core_anew.monitors.Monitor import Monitor
from tensorhive.core_anew.utils.decorators.override import override
from typing import Dict, List
import fabric
import invoke


class GPUMonitor(Monitor):
    _commands: Dict = {
        'list_gpus': 'nvidia-smi --list-gpus',
        # TODO Right now these commands receive output containing info about all gpus present... it is intended to query them by uuid and store under separate dict keys
        # 'process_statistics': 'nvidia-smi pmon --count 1 --id TODO_PUT_UUID',
        'gpu_uuid': 'nvidia-smi --query-gpu=gpu_uuid --format=csv,noheader',
        'memory.free': 'nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits',
        'memory.used': 'nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits',
        'memory.total': 'nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits',
        'temperature.gpu': 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'
        # add more commands here
    }

    @property
    def available_commands(self) -> Dict:
        return self._commands

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

    @override
    def update(self, connection_group) -> None:
        '''
        Attaches to given shell session,
        updates info about monitored resource,
        replaces old data (old state) with current
        '''
        # TODO Catch all errors
        # TODO Organize dict structure (see how fabric handles this)
        # FIXME Too many simplifications
        # DEBUG print(f'Benchmark with {len(connection_group)} nodes on {type(connection_group)}')
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
