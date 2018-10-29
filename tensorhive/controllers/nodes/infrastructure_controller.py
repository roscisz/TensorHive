from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from flask_jwt_extended import jwt_required


@jwt_required
def get_all_data():
    infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
    return infrastructure, 200


@jwt_required
def get_hostnames():
    infrastructure = TensorHiveManager().infrastructure_manager.infrastructure
    hostnames = infrastructure.keys()
    return list(hostnames), 200
