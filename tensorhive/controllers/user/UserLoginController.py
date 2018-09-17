from tensorhive.models.user.UserModel import UserModel
from connexion import NoContent
from flask_jwt_extended import create_access_token, create_refresh_token


class LoginUserController():
    # TODO Add more user parameters

    @staticmethod
    def login(user):
        current_user = UserModel.find_by_username(user['username'])
        if not current_user:
            # Duplicated resource
            return NoContent, 404

        if UserModel.verify_hash(user['password'], current_user.password):
            access_token = create_access_token(identity=user['username'])
            refresh_token = create_refresh_token(identity=user['username'])
            return {
                'msg': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        else:
            return {
                'msg': 'Incorrect credentials!'
            }, 401