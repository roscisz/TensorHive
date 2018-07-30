from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from connexion import NoContent


class GetMetricsController:
    @staticmethod
    def all():
        infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
        return infrastructure, 200

    @staticmethod
    def get(hostname: str, metric_type: str):
        try:
            infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
            metrics = infrastructure[hostname][metric_type]

            # If some data is unavailable, return [] (e.g. monitoring service got a connection exception),
            if isinstance(metrics, dict) and metrics.keys() & ['exception', 'exit_code']:
                metrics = []
            response = metrics, 200
        except KeyError:
            response = NoContent, 404
        finally:
            return response
