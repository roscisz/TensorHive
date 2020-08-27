from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from flask_jwt_extended import jwt_required
from tensorhive.models.Resource import Resource


def get_infrastructure():
    infrastructure = TensorHiveManager().infrastructure_manager.infrastructure

    # Try to save gpu resource to database
    try:
        resources = Resource.all()
        id_list = [resource.id for resource in resources]
        for hostname, value in infrastructure.items():
            gpu_list = value.get('GPU')
            if gpu_list is not None:
                for gpu_uuid, gpu_metrics in gpu_list.items():
                    if gpu_uuid not in id_list:
                        new_resource = Resource(
                            id=gpu_uuid,
                            name=gpu_metrics.get('name')
                        )
                        new_resource.save()
    except Exception:
        # In case of failure just return infrastructure
        pass

    return infrastructure


@jwt_required
def get_all_data():
    infrastructure = get_infrastructure()
    return infrastructure, 200


@jwt_required
def get_hostnames():
    infrastructure = get_infrastructure()
    hostnames = infrastructure.keys()
    return list(hostnames), 200
