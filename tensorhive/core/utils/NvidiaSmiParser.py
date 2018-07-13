from typing import Generator, Dict, List


class NvidiaSmiParser():
    @staticmethod
    def gpus_info_from_stdout(stdout: Generator) -> Dict[str, str]:
        '''
        Assumes nvidia-smi outputs with --format=csv (+must have a header)
        Example output:
        [
            {
                "name": "GeForce GTX 660",
                "fan.speed [%]": "37 %",
                ...
            }
            {
                "name": "GeForce GTX 780 Ti",
                "fan.speed [%]": "25 %"
                ...

            ]
        ]
        '''
        stdout_lines = list(stdout)  # type: List[str]
        assert stdout_lines, 'stdout is empty!'
        assert len(stdout_lines) > 1, 'stdout query result contains header only!'

        # Extract keys from nvidia-smi query result header
        header = stdout_lines[0]  # type: str
        gpu_parameters_keys = header.split(', ')  # type: List[str]

        # Extract stdout lines, where:  1 line = 1 GPU
        all_gpus_stdout_lines = stdout_lines[1:]  # type: List[str]

        # Result accumulator
        all_gpus_info = []  # type:List[Dict[str, str]]

        # Transform stdout of a single GPU and append to accumulator
        for single_gpu_result_line in all_gpus_stdout_lines:
            # Split by commas
            gpu_parameters_values = single_gpu_result_line.split(
                ', ')  # type: List[str]
            # Transform to dict
            single_gpu_info = dict(
                zip(gpu_parameters_keys, gpu_parameters_values))
            # Append
            all_gpus_info.append(single_gpu_info)
        return all_gpus_info
