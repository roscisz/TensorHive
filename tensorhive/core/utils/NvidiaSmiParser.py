from typing import Generator, Dict, List
import re
import logging
log = logging.getLogger(__name__)


class NvidiaSmiParser():
    '''Responsible for parsing output from commands executed by pssh'''

    key_mapping = {
        # keys: original nvidia-smi parameter names
        # values: simpler and shorter form
        'name': 'name',
        'uuid': 'uuid',
        'fan.speed [%]': 'fan_speed',
        'memory.free [MiB]': 'mem_free',
        'memory.used [MiB]': 'mem_used',
        'memory.total [MiB]': 'mem_total',
        'utilization.gpu [%]': 'gpu_util',
        'utilization.memory [%]': 'mem_util',
        'temperature.gpu': 'temp',
        'power.draw [W]': 'power'
    }

    @classmethod
    def make_dict(cls, keys, values):
        '''
        Creates a custom dictionary which uses shorter key names and
        
        Example keys and values:
        ['name', 'fan.speed [%]', 'utilization.gpu [%]', 'power.draw [W]']
        ['GeForce GTX 660', 32, null, 80]

        Example result:
        {
            "name": "GeForce GTX 660",
            "fan_speed": {'value': 32, 'unit': '%'},
            "gpu_util": {'value': null, 'unit': '%'},
            "power": {'value': 80, 'unit': 'W'},
            ...            
        }
        '''
        assert len(keys) == len(values), 'List sizes does not match.'
        values = cls._format_values(values)

        # Regex that matches: [W], [%], [MiB], etc.
        unit_regex = re.compile('[(.*)]$') 
        result = {}

        for (long_key_name, value) in zip(keys, values):
            short_key_name = cls.key_mapping[long_key_name]
            # Tries to find the unit inside original key name
            unit_found = unit_regex.match(long_key_name)

            if unit_found:
                # Matches % from [%], etc.
                unit = unit_found.group(1)
                result[short_key_name] = {'value': value, 'unit': unit}
            else:
                result[short_key_name] = value
        return result


    @classmethod
    def _format_values(cls, values: List[str]) -> List:
        '''Replaces plain string values returned by `nvidia-smi --query-gpu=...`'''
        def formatted_value(value):
            if value == '[Not Supported]':
                return None
            # TODO May want to handle floats also (currently they remain as strings)
            elif str.isdecimal(value):
                return int(value)
            else:
                return value

        # Apply formatting to each value
        return [formatted_value(v) for v in values]

    @classmethod
    def _renamed_keys(cls, original_keys: List[str]):
        '''Replaces key names returned by `nvidia-smi --query-gpu=...` with more compact alternatives'''
        try:
            new_keys = [cls.key_mapping[original_key] for original_key in original_keys]
            return new_keys
        except KeyError as unexisting_key:
            message = 'key mapping for {} not implemented!'.format(unexisting_key)
            log.critical(message)
            raise KeyError(message)

    @classmethod
    def parse_query_gpu_stdout(cls, stdout: Generator) -> Dict[str, Dict]:
        '''
        Example stdout:
        $ nvidia-smi --query-gpu=name,fan.speed,utilization.gpu --format=csv,nounits   
        name, fan.speed [%], utilization.gpu [%]
        GeForce GTX 660, 35, [Not Supported]

        Example result:
        {
            "GPU-d38d4de3-85ee-e837-3d87-e8e2faeb6a63": {
                "name": "GeForce GTX 660",
                "fan_speed": 32,
                "gpu_util": null,
                ...            
            }
        }
        '''
        stdout_lines = list(stdout)  # type: List[str]
        assert stdout_lines, 'stdout is empty!'
        assert len(stdout_lines) > 1, 'stdout query result contains header only!'

        # Extract keys from nvidia-smi query result header
        header = stdout_lines[0]  # type: str
        gpu_parameters_keys = header.split(', ')  # type: List[str]
        #gpu_parameters_keys = cls._renamed_keys(gpu_parameters_keys)

        # Extract stdout lines, where:  1 line = 1 GPU
        all_gpus_stdout_lines = stdout_lines[1:]  # type: List[str]

        # Define result accumulator
        result = {}  # type:Dict[str, Dict]

        # Transform each line (corresponding to a single GPU) and append to the accumulator
        for single_gpu_result_line in all_gpus_stdout_lines:
            # Split by commas
            gpu_parameters_values = single_gpu_result_line.split(', ')  # type: List[str]
            #gpu_parameters_values = cls._format_values(gpu_parameters_values)  # type: List

            query_results_for_single_gpu = csl.make_dict(gpu_parameters_keys, gpu_parameters_values)
            # Transform two lists into dictionary by zipping the keys with corresponding values
            #query_results_for_single_gpu = dict(zip(gpu_parameters_keys, gpu_parameters_values))

            # Move UUID outside the dict
            uuid = query_results_for_single_gpu.pop('uuid')  # type: str

            # Assign query results to that key
            result[uuid] = query_results_for_single_gpu
        #import json
        #log.debug('\n{}\n'.format(json.dumps(result, indent=2)))
        return result

    @classmethod
    def parse_pmon_stdout(cls, stdout: Generator) -> Dict[str, Dict]:
        '''
        Assumming: 
        nvidia-smi --query-gpu=uuid --format=csv,noheader | while read line; do
            echo "UUID=$line"
            nvidia-smi pmon --count 1 --id "$line"
        done

        Example command output (input for this method):

        # gpu     pid  type    sm   mem   enc   dec   command
        # Idx       #   C/G     %     %     %     %   name
            0    4810     G     0     0     0     0   Xorg           
            0    7187     G     0     0     0     0   compiz         
            0   16250     C    83    99     0     0   python         
            1   23335     C     0     0     0     0   python         
            1   31381     C    33    53     0     0   python         
            2   19635     C    39    35     0     0   python         
            3   33317     C    31    11     0     0   python 

        Result:
        {
            '<UUID>': {
                'processes': [
                    {
                        'gpu': 0, 
                        'pid': 4810, 
                        'type': 'G', 
                        'sm': 0, 
                        'mem': 0, 
                        'enc': 0, 
                        'dec': 0, 
                        'command': 'Xorg'
                    }, 
                    ...
                ]
            }
        }
        Result:
        [
            {
                'uuid': '<UUID>',
                'pid': 4810, 
                'command': 'Xorg',
                ...
            },
            ...
        ]
        '''
        stdout_lines = list(stdout)
        assert stdout_lines, 'stdout is empty!'
        assert len(stdout_lines) > 2, 'pmon\'s stdout should return at least 3 lines'

        

        '''
        stdout_lines[0]:
        '# gpu        pid  type    sm   mem   enc   dec   command'
        (We want to skip '#' -> not a key)

        keys:
        ['gpu', 'pid', 'type', 'sm', 'mem', 'enc', 'dec', 'command']
        
        lines:
        ['0    4810     G     0     0     0     0   Xorg',
        '0    7187     G     0     0     0     0   compiz']
        '''
        def minified_process_dict(original: Dict) -> Dict:
            return {
                'uuid': original['uuid'],
                'pid': original['pid'],
                'command': original['command']
            }

        uuid_regex = re.compile('^UUID=(.*)$')
        stdout_of_all_gpus = {}
        for line in list(stdout_lines):
            uuid_match = uuid_regex.match(line)
            if uuid_match:
                uuid = uuid_match.group(1)
                stdout_of_all_gpus[uuid] = []
            else:
                stdout_of_all_gpus[uuid].append(line)

        processes = []
        for uuid, single_gpu_stdout_lines in stdout_of_all_gpus.items():
            header = single_gpu_stdout_lines[0][2:]
            keys = header.split()
            processes_lines = single_gpu_stdout_lines[2:]

            for line in processes_lines:
                values = line.split()
                values = cls._format_values(values)

                full_process_info = dict(zip(keys, values))
                full_process_info['uuid'] = uuid

                process = minified_process_dict(full_process_info)
                processes.append(process)

        # import json
        # log.debug('\n{}\n'.format(json.dumps(processes, indent=2)))

        return processes
            
                
        
