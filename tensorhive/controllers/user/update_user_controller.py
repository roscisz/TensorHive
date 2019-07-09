from tensorhive.models.User import User
from tensorhive.config import API
from tensorhive.authorization import admin_required
from tensorhive.models.Role import Role
from flask_jwt_extended import jwt_required

R = API.RESPONSES['user']
G = API.RESPONSES['general']


@admin_required
@jwt_required
def update(user):
    print('REQ', user)
    if user.get('id') is not None:
        try:
            found_user = User.get(user['id'])
            updateable_field_names = ['username', 'password', 'email']

            for field_name in updateable_field_names:
                if user.get(field_name) is not None:
                    if field_name == 'roles':
                        new_value = [Role(name=role_name) for role_name in user['roles']]
                    else:
                        new_value = user[field_name]
                    setattr(found_user, field_name, new_value)

            found_user.save()
        except AssertionError as e:
            content = {'msg': R['update']['failure']['invalid'].format(reason=e)}
            status = 422
        except Exception:
            content = {'msg': G['internal_error']}
            status = 500
        else:
            content = {'msg': R['update']['success'], 'reservation': found_user.as_dict}
            status = 201
    else:
        content = {'msg': G['bad_request']}
        status = 400

    return content, status
