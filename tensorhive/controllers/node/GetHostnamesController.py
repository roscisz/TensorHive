from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from connexion import NoContent


class GetHostnamesController:
    @staticmethod
    def get():
        infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
        hostnames = infrastructure.keys()
        return list(hostnames), 200
