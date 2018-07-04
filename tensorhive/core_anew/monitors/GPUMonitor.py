from tensorhive.core_anew.monitors.Monitor import Monitor
from typing import Dict, List
import spur

class GPUMonitor(Monitor):
    _commands: Dict = {
        'list_gpus': 'nvidia-smi --list-gpus',
        #TODO below
        #'process_statistics': 'nvidia-smi pmon --count 1 --id TODO_PUT_UUID',
        'memory.free': 'nvidia-smi --query-gpu=memory.free --format=csv,noheader',
        'memory.used': 'nvidia-smi --query-gpu=memory.used --format=csv,noheader',
        'memory.total': 'nvidia-smi --query-gpu=memory.total --format=csv,noheader',
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

    #@override
    def update(self, connection) -> None:
        '''
        Attaches to given shell session,
        updates info about monitored resource,
        replaces old data (old state) with current
        '''
        with connection:
            # e.g. can loop through all commands (depending on selected monitoring mode)

            for command_key, command_str in self.available_commands.items():
                try:
                    shell_command = command_str.split(' ')
                    result = connection.run(shell_command, allow_error=False)
                    output = result.output.decode('utf-8').rstrip('\n')
                    self.gathered_data[command_key] = output
                except(spur.results.RunProcessError, 
                        spur.CouldNotChangeDirectoryError, 
                        spur.NoSuchCommandError) as e:
                    print('Spur ERROR! message:\n{msg}\n'.format(msg=e))

    

  