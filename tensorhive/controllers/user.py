import logging
import socket
from typing import Any, Dict, List, Tuple, Union
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_raw_jwt
from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_claims
from paramiko.client import SSHClient, WarningPolicy
from paramiko.ssh_exception import AuthenticationException, BadHostKeyException, SSHException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.authorization import admin_required
from tensorhive.config import API, APP_SERVER, SSH
from tensorhive.core.managers.TensorHiveManager import TensorHiveManager
from tensorhive.models.RevokedToken import RevokedToken
from tensorhive.models.Role import Role
from tensorhive.models.User import User
from tensorhive.models.Group import Group

log = logging.getLogger(__name__)
GENERAL = API.RESPONSES['general']
USER = API.RESPONSES['user']
TOKEN = API.RESPONSES['token']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
UserId = int


@jwt_required
def get() -> Tuple[List[Any], HttpStatusCode]:
    claims = get_jwt_claims()
    include_private = 'admin' in claims['roles']

    return [
        user.as_dict(include_private=include_private) for user in User.all()
    ], 200


@jwt_required
def get_by_id(id: UserId) -> Tuple[Content, HttpStatusCode]:
    try:
        user = User.get(id)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': USER['not_found']}, 404
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        current_user_id = get_jwt_identity()
        claims = get_jwt_claims()
        include_private = 'admin' in claims['roles'] or id == current_user_id

        content, status = {'msg': USER['get']['success'], 'user': user.as_dict(include_private=include_private)}, 200
    finally:
        return content, status


def do_create(user: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        new_user = User(
            username=user['username'],
            email=user['email'],
            password=user['password'],
            roles=[Role(name='user')]
        )
        new_user.save()

        try:
            default_groups = Group.get_default_groups()
            for group in default_groups:
                group.add_user(new_user)
        except Exception:
            log.warning("User has been created, but not added to default group.")
    except AssertionError as e:
        content = {'msg': USER['create']['failure']['invalid'].format(reason=e)}
        status = 422
    except IntegrityError:
        content = {'msg': USER['create']['failure']['duplicate']}
        status = 409
    except Exception as e:
        content = {'msg': GENERAL['internal_error'] + str(e)}
        status = 500
    else:
        content = {
            'msg': USER['create']['success'],
            'user': new_user.as_dict(include_private=True)
        }
        status = 201
    finally:
        return content, status


@admin_required
def create(newUser: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    return do_create(newUser)


def ssh_signup(user: Dict[str, Any]) -> Tuple[Union[str, List[Any], Content], HttpStatusCode]:
    # TODO: configure nodes used for authentication
    auth_node = next(iter(SSH.AVAILABLE_NODES))

    ssh_key = TensorHiveManager().dedicated_ssh_key
    test_client = SSHClient()
    test_client.load_system_host_keys()
    test_client.set_missing_host_key_policy(WarningPolicy())

    try:
        test_client.connect(auth_node, username=user['username'], pkey=ssh_key)
    except AuthenticationException:
        return {'msg': GENERAL['unprivileged']}, 403
    except (BadHostKeyException, SSHException, socket.error) as e:
        return 'An error occurred while authenticating: {}'.format(e), 500
    finally:
        test_client.close()

    return do_create(user)


def authorized_keys_entry() -> str:
    key = TensorHiveManager().dedicated_ssh_key.get_base64()
    return 'ssh-rsa {} tensorhive@{}'.format(key, APP_SERVER.HOST)


@admin_required
def update(newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    user = newValues
    print('REQ', user)
    if user.get('id') is not None:
        try:
            found_user = User.get(user['id'])
            updatable_field_names = ['username', 'password', 'email']

            for field_name in updatable_field_names:
                if user.get(field_name) is not None:
                    if field_name == 'roles':
                        new_value = [Role(name=role_name) for role_name in user['roles']]
                    else:
                        new_value = user[field_name]
                    setattr(found_user, field_name, new_value)

            found_user.save()
        except AssertionError as e:
            content = {'msg': USER['update']['failure']['invalid'].format(reason=e)}
            status = 422
        except Exception:
            content = {'msg': GENERAL['internal_error']}
            status = 500
        else:
            content = {'msg': USER['update']['success'], 'reservation': found_user.as_dict(include_private=True)}
            status = 201
    else:
        content = {'msg': GENERAL['bad_request']}
        status = 400

    return content, status


@admin_required
def delete(id: UserId) -> Tuple[Content, HttpStatusCode]:
    try:
        current_user_id = get_jwt_identity()

        # User is not allowed to delete his own account
        assert id != current_user_id, USER['delete']['self']

        # Fetch the user and destroy
        user_to_destroy = User.get(id)
        user_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, 403
    except NoResultFound:
        content, status = {'msg': USER['not_found']}, 404
    except Exception as e:
        content, status = {'msg': GENERAL['internal_error'] + str(e)}, 500
    else:
        content, status = {'msg': USER['delete']['success']}, 200
    finally:
        return content, status


def login(user: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        current_user = User.find_by_username(user['username'])
        assert User.verify_hash(user['password'], current_user.password), \
            USER['login']['failure']['credentials']
    except NoResultFound:
        content = {'msg': USER['not_found']}
        status = 404
    except AssertionError as error_message:
        content = {'msg': str(error_message)}
        status = 401
    except Exception:
        content = {'msg': GENERAL['internal_error']}
        status = 500
    else:
        content = {
            'msg': USER['login']['success'].format(username=current_user.username),
            'access_token': create_access_token(identity=current_user.id, fresh=True),
            'refresh_token': create_refresh_token(identity=current_user.id)
        }
        status = 200
    finally:
        return content, status


def logout(token_type: str) -> Tuple[Content, HttpStatusCode]:
    jti = get_raw_jwt()['jti']
    try:
        RevokedToken(jti=jti).save()
    except Exception:
        log.critical(GENERAL['internal_error'])
        log.critical(TOKEN['revoke']['failure'].format(token_type=token_type))
        content = {'msg': GENERAL['internal_error']}
        status = 500
    else:
        content = {'msg': USER['logout']['success']}
        status = 200
    finally:
        return content, status


@jwt_required
def logout_with_access_token() -> Tuple[Content, HttpStatusCode]:
    return logout('Access')


@jwt_refresh_token_required
def logout_with_refresh_token() -> Tuple[Content, HttpStatusCode]:
    return logout('Refresh')


@jwt_refresh_token_required
def generate() -> Tuple[Content, HttpStatusCode]:
    new_access_token = create_access_token(identity=get_jwt_identity(), fresh=False)
    content = {
        'msg': TOKEN['refresh']['success'],
        'access_token': new_access_token
    }
    return content, 200
