from tensorhive.models.User import User
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
R = API.RESPONSES['user']
G = API.RESPONSES['general']


def login(user):
    try:
        current_user = User.find_by_username(user['username'])
        assert User.verify_hash(user['password'], current_user.password), \
            R['login']['failure']['credentials']
    except NoResultFound:
        content = {'msg': R['not_found']}
        status = 404
    except AssertionError as error_message:
        content = {'msg': str(error_message)}
        status = 401
    except Exception:
        content = {'msg': G['internal_error']}
        status = 500
    else:
        content = {
            'msg': R['login']['success'].format(username=current_user.username),
            'access_token': create_access_token(identity=current_user.id, fresh=True),
            'refresh_token': create_refresh_token(identity=current_user.id)
        }
        status = 200
    finally:
        return content, status
