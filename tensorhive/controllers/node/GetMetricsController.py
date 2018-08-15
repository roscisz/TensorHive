from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from connexion import NoContent


class GetMetricsController:
    @staticmethod
    def all():
        infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
        return infrastructure, 200

    @staticmethod
    def get(hostname: str, resource_type: str, metric_type: str = None):
        try:
            infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
            resource_data = infrastructure[hostname][resource_type]

            if resource_type == 'GPU':
                '''
                Create a dictionary, where each key contains GPU's UUID
                and the corresponding value is the actual metric data

                Example (metric_type is None):
                { 
                    '<GPU0_UUID>': {'fan_speed': 31, 'util': 20, ...},
                    '<GPU1_UUID>': {'fan_speed': 32, 'util': 25, ...},
                }

                Example (metric_type == 'fan_speed'):
                { 
                    '<GPU0_UUID>': 31,
                    '<GPU1_UUID>': 32,
                }
                '''
                if metric_type is None:
                    # Put all gathered metric data for each GPU
                    result = {gpu['uuid']: gpu for gpu in resource_data}
                else:
                    # Put only requested metric data for each GPU
                    result = {gpu['uuid']: gpu[metric_type] for gpu in resource_data}

            # TODO Put exception and error messages within infrastructure dict, so it can be passed to the API consumer
            response = result, 200
        except KeyError:
            response = NoContent, 404
        finally:
            return response
