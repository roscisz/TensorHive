from tensorhive.controllers.node.GetMetricsController import GetMetricsController
from tensorhive.controllers.node.GetHostnamesController import GetHostnamesController
from connexion import NoContent


def get_hostnames():
    return GetHostnamesController.get()


def get_all_metrics():
    return GetMetricsController.all()


def get_gpu_metrics(hostname: str, metric_type: str = None):
    return GetMetricsController.get(hostname=hostname,
                                    resource_type='GPU',
                                    metric_type=metric_type)
