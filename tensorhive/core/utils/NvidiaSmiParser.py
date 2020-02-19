from typing import Generator, Dict, List
import re
import logging
log = logging.getLogger(__name__)


class NvidiaSmiParser():
    '''Responsible for parsing output from commands executed by pssh'''
    include_units = True
    key_mapping = {
        # keys: original nvidia-smi parameter names
        # values: simpler and shorter form
        'name': 'name',
        'uuid': 'uuid',
        'index': 'index',
        'fan.speed [%]': 'fan_speed',
        'memory.free [MiB]': 'mem_free',
        'memory.used [MiB]': 'mem_used',
        'memory.total [MiB]': 'mem_total',
        'utilization.gpu [%]': 'utilization',
        'utilization.memory [%]': 'mem_util',
        'temperature.gpu': 'temp',
        'power.draw [W]': 'power'
    }

    @classmethod
    def make_dict(cls, keys: List[str], values: List[str]) -> Dict:
        '''
        Builds a custom dictionary which uses shorter key names and

        Example keys and values:
        ['name', 'fan.speed [%]', 'utilization.gpu [%]', 'power.draw [W]']
        ['GeForce GTX 660', 32, null, 80]

        Example result with enabled units:
        {
            "name": "GeForce GTX 660",
            "fan_speed": {'value': 32, 'unit': '%'},
            "gpu_util": {'value': null, 'unit': '%'},
            "power": {'value': 80, 'unit': 'W'},
            ...
        }

        Example result with disabled units:
        {
            "name": "GeForce GTX 660",
            "fan_speed": 32,
            "gpu_util": null,
            "power": 80,
            ...
        }
        '''
        assert len(keys) == len(values), 'List sizes does not match.'
        values = cls._format_values(values)

        # Regex that matches: [W], [%], [MiB], etc. at the end of string
        unit_regex = re.compile(r'\[(.*)\]$')
        result = {}

        for (long_key_name, value) in zip(keys, values):
            short_key_name = cls._shorter_key_name(long_key_name)
            # Tries to find the unit inside original key name
            unit_found = unit_regex.search(long_key_name)

            if unit_found and cls.include_units is True:
                # Matches % from [%], etc.
                unit = unit_found.group(1)
                result[short_key_name] = {'value': value, 'unit': unit}
            else:
                # If there's no unit provided, just assign the value
                result[short_key_name] = value  # type: ignore
        return result

    @classmethod
    def _format_values(cls, values: List[str]) -> List:
        '''
        Replaces string values returned by `nvidia-smi --query-gpu=...`
        Main goal is to handle [Not Supported] and when possible, cast str to int/float
        '''
        def formatted_value(value):
            if value == '[Not Supported]':
                return None
            # TODO May want to handle floats also (currently they remain as strings)
            elif str.isdecimal(value):
                return int(value)
            else:
                return value

        return [formatted_value(v) for v in values]

    @classmethod
    def _shorter_key_name(cls, original_key: str):
        try:
            return cls.key_mapping[original_key]
        except KeyError as unexisting_key:
            message = 'Key mapping for {} not implemented!'.format(unexisting_key)
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

        # Extract stdout lines, where:  1 line = 1 GPU
        all_gpus_stdout_lines = stdout_lines[1:]  # type: List[str]

        result = {}  # type:Dict[str, Dict]

        # Transform each line (corresponding to a single GPU) and append to the accumulator
        for single_gpu_result_line in all_gpus_stdout_lines:
            # Split by commas
            gpu_parameters_values = single_gpu_result_line.split(', ')  # type: List[str]
            query_results_for_single_gpu = cls.make_dict(
                gpu_parameters_keys, gpu_parameters_values)

            # Separate some keys that are not metrics
            uuid = query_results_for_single_gpu.pop('uuid')  # type: str
            name = query_results_for_single_gpu.pop('name')
            index = query_results_for_single_gpu.pop('index')

            result[uuid] = {}
            result[uuid]['name'] = name
            result[uuid]['index'] = index
            result[uuid]['metrics'] = query_results_for_single_gpu

        return result

    @classmethod
    def parse_pmon_stdout(cls, stdout: Generator) -> List[Dict]:
        '''
        Example of expected stdout:
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
        and so on...

        Example result:
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
        assert len(stdout_lines) >= 2, 'pmon\'s stdout should return at least 2 lines'

        def minified_process_dict(original: Dict) -> Dict:
            # Returns a dict which contains only the essential keys
            return {
                'uuid': original['uuid'],
                'pid': original['pid'],
                'command': original['command']
            }

        # Parse whole stdout and split it into chunks.
        # Each chunk is transformed into a dictionary.
        # key=UUID, value=pmon's stdout lines corresponding GPU witch such UUID
        uuid_regex = re.compile('^UUID=(.*)$')
        stdout_of_all_gpus = {}  # type: Dict
        for line in list(stdout_lines):
            uuid_match = uuid_regex.match(line)
            if uuid_match:
                uuid = uuid_match.group(1)
                # Initialize with default value
                stdout_of_all_gpus[uuid] = []
            else:
                # Two types of stdout for a single GPU
                if line == '[PMON NOT SUPPORTED]':
                    # Replace [] with None (rare cases)
                    stdout_of_all_gpus[uuid] = None
                else:
                    stdout_of_all_gpus[uuid].append(line)

        # Now parse pmon's stdout for each GPU
        # Transform each parsed process into dictionary and append to the list
        processes = []
        for uuid, single_gpu_stdout_lines in stdout_of_all_gpus.items():

            # nvidia-smi pmon failed on this GPU => no processes to parse
            if single_gpu_stdout_lines is None:
                continue

            '''
            single_gpu_stdout_lines[0]:
            '# gpu        pid  type    sm   mem   enc   dec   command'
            (We want to skip '#' -> not a key, hence [0][2:])

            keys:
            ['gpu', 'pid', 'type', 'sm', 'mem', 'enc', 'dec', 'command']

            processes_lines:
            ['0    4810     G     0     0     0     0   Xorg',
            '0    7187     G     0     0     0     0   compiz']
            '''
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

        return processes
