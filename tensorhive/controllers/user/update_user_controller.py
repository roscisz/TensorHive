from tensorhive.models.User import User
from tensorhive.config import API
from tensorhive.authorization import admin_required
from tensorhive.models.Role import Role
from flask_jwt_extended import jwt_required

R = API.RESPONSES['user']
G = API.RESPONSES['general']


@admin_required
def update(user):
    if user.get('id') is not None:
        try:
            found_user = User.get(user['id'])
            found_user.username = user['username'] if user.get('username') is not None else found_user.username
            if user.get('password') is not None:
                found_user.password = user['password']
            if user.get('roles') is not None:
                roles = [Role(name=role_name) for role_name in user['roles']]
                found_user.roles = roles
            found_user.save()

        except AssertionError as e:
            content = {'msg': R['update']['failure']['invalid'].format(reason=e)}
            status = 422
        except Exception:
            content = {'msg': G['internal_error']}
            status = 500
        else:
            content = {
                'msg': R['update']['success'],
                'reservation': found_user.as_dict
            }
            status = 201
    else:
            content = {'msg': G['bad_request']}
            status = 400

    return content, status
