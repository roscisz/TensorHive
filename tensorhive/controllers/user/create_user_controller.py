from sqlalchemy.exc import IntegrityError
from tensorhive.models.User import User
from tensorhive.models.Role import Role
from tensorhive.database import db, flask_app
from flask_jwt_extended import get_jwt_identity
from tensorhive.config import API
from tensorhive.authorization import admin_required
R = API.RESPONSES['user']
G = API.RESPONSES['general']


@admin_required
def create(user):
    try:
        # Check identity
        current_user_id = get_jwt_identity()
        assert current_user_id, G['no_identity']

        with flask_app.app_context():
            # Check if the identity exists
            current_user = User.get(current_user_id)
            db.session.add(current_user)

            # Check permissions
            assert current_user.has_role('admin'), G['unpriviliged']                           

            # Try to create with default role
            new_user = User(username=user['username'],
                            password=user['password'],
                            roles=[Role(name='user')])
            new_user.save()
    except AssertionError as e:
        content = {'msg': str(e)}
        status = 403
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
