from sqlalchemy.exc import IntegrityError
from tensorhive.models.User import User
from tensorhive.models.Role import Role
from paramiko.client import SSHClient, WarningPolicy
from paramiko.ssh_exception import AuthenticationException, BadHostKeyException, SSHException
import socket
from tensorhive.database import db_session
from flask_jwt_extended import get_jwt_identity
from tensorhive.config import API
from tensorhive.config import APP_SERVER
from tensorhive.authorization import admin_required
from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from tensorhive.config import SSH
R = API.RESPONSES['user']
G = API.RESPONSES['general']


def do_create(user):
    try:
        new_user = User(
            username=user['username'],
            email=user['email'],
            password=user['password'],
            roles=[Role(name='user')]
        )
        new_user.save()
    except AssertionError as e:
        content = {'msg': R['create']['failure']['invalid'].format(reason=e)}
        status = 422
    except IntegrityError:
        content = {'msg': R['create']['failure']['duplicate']}
        status = 409
    except Exception as e:
        content = {'msg': G['internal_error'] + str(e)}
        status = 500
    else:
        content = {
            'msg': R['create']['success'],
            'user': new_user.as_dict
        }
        status = 201
    finally:
        return content, status


@admin_required
def create(user):
    return do_create(user)


def ssh_signup(user):
    # TODO: configure nodes used for authentication
    auth_node = next(iter(SSH.AVAILABLE_NODES))

    ssh_key = TensorHiveManager().dedicated_ssh_key
    test_client = SSHClient()
    test_client.load_system_host_keys()
    test_client.set_missing_host_key_policy(WarningPolicy())

    try:
        test_client.connect(auth_node, username=user['username'], pkey=ssh_key)
    except AuthenticationException:
        return {'msg': G['unpriviliged']}, 403
    except (BadHostKeyException, SSHException, socket.error) as e:
        return 'An error ocurred while authenticating: {}'.format(e), 500
    finally:
        test_client.close()

    return do_create(user)


def authorized_keys_entry():
    key = TensorHiveManager().dedicated_ssh_key.get_base64()
    return 'ssh-rsa {} tensorhive@{}'.format(key, APP_SERVER.HOST)
