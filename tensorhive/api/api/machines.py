from tensorhive.core.managers.TensorHiveManager import TensorHiveManager


def search():
    return list(TensorHiveManager().infrastructure_manager.infrastructure.keys())
