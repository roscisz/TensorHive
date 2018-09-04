from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from connexion import NoContent


class GetGPUController:
    @staticmethod
    def all():
        infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
        return infrastructure, 200

    @staticmethod
    def get_metrics(hostname: str, metric_type: str = None):
        try:
            infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
            resource_data = infrastructure[hostname]['GPU']

            '''
            Create a dictionary, where each key contains GPU's UUID
            and the corresponding value is the actual metric data

            Example (metric_type is None + disabled units):
            { 
                '<GPU0_UUID>': {'fan_speed': 31, 'util': 20, ...},
                '<GPU1_UUID>': {'fan_speed': 32, 'util': 25, ...},
            }

            Example (metric_type == 'fan_speed' with enabled units):
            { 
                '<GPU0_UUID>': {'value': 31, 'unit': '%'},
                '<GPU1_UUID>': {'value': 32, 'unit': '%'},
            }
            '''
            if resource_data is None:
                # No data about GPU
                response = NoContent, 404
            else:
                if metric_type is None:
                    # Put all gathered metric data for each GPU
                    result = {uuid: gpu_data['metrics'] for uuid, gpu_data in resource_data.items()}
                else:
                    # Put only requested metric data for each GPU
                    result = {uuid: gpu_data['metrics'][metric_type] for uuid, gpu_data in resource_data.items()}
                response = result, 200

            # TODO Put exception and error messages within infrastructure dict, so it can be passed to the API consumer
        except KeyError:
            response = NoContent, 404
        finally:
            return response


    @staticmethod
    def get_processes(hostname: str):
        try:
            infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
            resource_data = infrastructure[hostname]['GPU']
            result = {uuid: gpu_data['processes'] for uuid, gpu_data in resource_data.items()}
            response = result, 200
        except KeyError:
            response = NoContent, 404
        finally:
            return response
    
    @staticmethod
    def get_info(hostname: str):
        try:
            infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
            resource_data = infrastructure[hostname]['GPU']

            def basic_info(full_dict):
                return {
                    'name': full_dict['name'],
                    'index': full_dict['index']
                }

            result = {uuid: basic_info(gpu_data) for uuid, gpu_data in resource_data.items()}
            response = result, 200
        except KeyError:
            response = NoContent, 404
        finally:
            return response