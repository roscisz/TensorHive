from sqlalchemy.exc import IntegrityError
from tensorhive.models.User import User
from tensorhive.models.Role import Role
from tensorhive.database import db_session
from flask_jwt_extended import get_jwt_identity
from tensorhive.config import API
from tensorhive.authorization import admin_required
R = API.RESPONSES['user']
G = API.RESPONSES['general']


@admin_required
def create(user):
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
