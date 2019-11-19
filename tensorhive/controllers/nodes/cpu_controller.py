from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from connexion import NoContent
from flask_jwt_extended import jwt_required


@jwt_required
def get_metrics(hostname: str, metric_type: str = None):
    try:
        infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
        resource_data = infrastructure[hostname]['CPU']

        # No data about GPU
        assert resource_data

        if metric_type is None:
            # Put all gathered metric data for each GPU
            result = {uuid: cpu_data['metrics'] for uuid, cpu_data in resource_data.items()}
        else:
            # Put only requested metric data for each GPU
            result = {uuid: gpu_data['metrics'][metric_type] for uuid, gpu_data in resource_data.items()}
    except (KeyError, AssertionError):
        content, status = NoContent, 404
    else:
        content, status = result, 200
    finally:
        return content, status
