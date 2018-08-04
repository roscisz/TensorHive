from tensorhive.controllers.node.GetMetricsController import GetMetricsController
from tensorhive.controllers.node.GetHostnamesController import GetHostnamesController
from connexion import NoContent


def get_hostnames():
    return GetHostnamesController.get()


def get_all_metrics():
    return GetMetricsController.all()


def get_gpu_metrics(hostname: str, metric_type: str = None):
    query_to_key_mapping = {
        'name': 'name',
        'uuid': 'uuid',
        'fan': 'fan.speed [%]',
        'mem_free': 'memory.free [MiB]',
        'mem_used': 'memory.used [MiB]',
        'mem_total': 'memory.total [MiB]',
        'util': 'utilization.gpu [%]',
        'mem_util': 'utilization.memory [%]',
        'temp': 'temperature.gpu',
        'power': 'power.draw [W]'
    }
    if metric_type is not None:
        metric_type = query_to_key_mapping[metric_type]
    return GetMetricsController.get(hostname=hostname,
                                    resource_type='GPU',
                                    metric_type=metric_type)
