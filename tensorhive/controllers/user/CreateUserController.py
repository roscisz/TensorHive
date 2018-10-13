from sqlalchemy.exc import IntegrityError
from tensorhive.models.User import User
from tensorhive.models.Role import Role
from tensorhive.database import db, flask_app
from flask_jwt_extended import get_jwt_identity
from tensorhive.config import API
R = API.RESPONSES['user']
G = API.RESPONSES['general']


class CreateUserController():

    @staticmethod
    def create(user):
        try:
            current_user_id = get_jwt_identity()
            assert current_user_id, G['no_identity']

            with flask_app.app_context():
                # Admin priviliges are required
                current_user = User.get(current_user_id)
                db.session.add(current_user)
                assert current_user.has_role('admin'), G['unpriviliged']                           

                # Create
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
