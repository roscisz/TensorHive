from tensorhive.controllers.node.GetMetricsController import GetMetricsController
from tensorhive.controllers.node.GetHostnamesController import GetHostnamesController
from connexion import NoContent


def get_hostnames():
    return GetHostnamesController.get()


def get_all_metrics():
    return GetMetricsController.all()


def get_gpu_metrics(hostname):
    return GetMetricsController.gpu(hostname=hostname, metric_type='GPU')


def get_gpu_fan(hostname):
    return GetMetricsController.get(hostname=hostname, metric_type='GPU', parameter_name='fan.speed [%]')
