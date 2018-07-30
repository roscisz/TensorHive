from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from connexion import NoContent

# TODO Move the logic to controllers
def get_hostnames():
    infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
    hostnames = infrastructure.keys()
    return list(hostnames), 200

def get_all_metrics():
    infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
    return infrastructure, 200

def get_gpu_metrics(hostname):
    try:
        infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
        metrics = infrastructure[hostname]['GPU']

        # If some data is unavailable, return [] (e.g. monitoring service got a connection exception),
        if isinstance(metrics, dict) and metrics.keys() & ['exception', 'exit_code']:
            metrics = []
        response = metrics, 200
    except KeyError:
        response = NoContent, 404
    finally:
        return response