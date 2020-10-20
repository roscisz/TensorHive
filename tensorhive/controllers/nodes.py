from connexion import NoContent
from flask_jwt_extended import jwt_required
from tensorhive.config import API
from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from tensorhive.models.Resource import Resource

NODES = API.RESPONSES['nodes']


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
                            name=gpu_metrics.get('name'),
                            hostname=hostname
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


@jwt_required
def get_cpu_metrics(hostname: str, metric_type: str = None):
    try:
        infrastructure = get_infrastructure()
        resource_data = infrastructure[hostname]['CPU']

        # No data about GPU
        assert resource_data

        if metric_type is None:
            # Put all gathered metric data for each GPU
            result = {uuid: cpu_data['metrics'] for uuid, cpu_data in resource_data.items()}
        else:
            # Put only requested metric data for each GPU
            result = {uuid: gpu_data['metrics'][metric_type] for uuid, gpu_data in resource_data.items()}
    except (KeyError, AssertionError):
        content, status = NoContent, 404
    else:
        content, status = result, 200
    finally:
        return content, status


@jwt_required
def get_gpu_metrics(hostname: str, metric_type: str = None):
    try:
        infrastructure = get_infrastructure()
        resource_data = infrastructure[hostname]['GPU']

        '''
        Create a dictionary, where each key contains GPU's UUID
        and the corresponding value is the actual metric data

        Example (metric_type is None + disabled units):
        {
            '<GPU0_UUID>': {'fan_speed': 31, 'util': 20, ...},
            '<GPU1_UUID>': {'fan_speed': 32, 'util': 25, ...},
        }

        Example (metric_type == 'fan_speed' with enabled units):
        {
            '<GPU0_UUID>': {'value': 31, 'unit': '%'},
            '<GPU1_UUID>': {'value': 32, 'unit': '%'},
        }
        '''
        # No data about GPU
        assert resource_data

        if metric_type is None:
            # Put all gathered metric data for each GPU
            result = {uuid: gpu_data['metrics'] for uuid, gpu_data in resource_data.items()}
        else:
            # Put only requested metric data for each GPU
            result = {uuid: gpu_data['metrics'][metric_type] for uuid, gpu_data in resource_data.items()}
    except (KeyError, AssertionError):
        content, status = NoContent, 404
    else:
        content, status = result, 200
    finally:
        return content, status


# @jwt_required
def get_gpu_processes(hostname: str):
    try:
        infrastructure = get_infrastructure()
        resource_data = infrastructure[hostname]['GPU']
        result = {uuid: gpu_data['processes'] for uuid, gpu_data in resource_data.items()}
        response = result, 200
    except KeyError:
        response = NoContent, 404
    finally:
        return response


@jwt_required
def get_gpu_info(hostname: str):
    try:
        infrastructure = get_infrastructure()
        resource_data = infrastructure[hostname]['GPU']

        def basic_info(full_dict):
            return {
                'name': full_dict['name'],
                'index': full_dict['index']
            }
        # TODO Should be wrapped into dict: {'msg': 'OK', 'info': content}
        content = {uuid: basic_info(gpu_data) for uuid, gpu_data in resource_data.items()}
        status = 200
    except KeyError:
        # TODO Theoretically possible that ['GPU'] can trigger this exception
        content = {'msg': NODES['hostname']['not_found']}
        status = 404
    finally:
        return content, status
