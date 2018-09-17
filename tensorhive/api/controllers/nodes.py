from tensorhive.controllers.node.GetGPUController import GetGPUController
from tensorhive.controllers.node.GetHostnamesController import GetHostnamesController
from flask_jwt_extended import jwt_required

@jwt_required
def get_hostnames():
    return GetHostnamesController.get()

@jwt_required
def get_all_metrics():
    return GetGPUController.all()

@jwt_required
def get_gpu_metrics(hostname: str, metric_type: str = None):
    return GetGPUController.get_metrics(hostname=hostname,
                                    metric_type=metric_type)
@jwt_required
def get_gpu_processes(hostname: str):
    return GetGPUController.get_processes(hostname=hostname)

@jwt_required
def get_gpu_info(hostname: str):
    return GetGPUController.get_info(hostname=hostname)