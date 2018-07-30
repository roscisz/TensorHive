from tensorhive.controllers.node.GetMetricsController import GetMetricsController
from tensorhive.controllers.node.GetHostnamesController import GetHostnamesController
from connexion import NoContent


def get_hostnames():
    return GetHostnamesController.get()


def get_all_metrics():
    return GetMetricsController.all()


def get_gpu_metrics(hostname):
    return GetMetricsController.get(hostname=hostname, metric_type='GPU')
