from tensorhive.models.user.UserModel import UserModel
from connexion import NoContent
from flask_jwt_extended import create_access_token, create_refresh_token


class CreateUserController():
    # TODO Add authentication, uniqueness checks
    # TODO Add more user parameters

    @staticmethod
    def register(user):
        if UserModel.find_by_username(user['username']):
            # Duplicated resource
            return NoContent, 409

        new_user = UserModel(
            username=user['username'],
            password=UserModel.generate_hash(user['password'])
            # TODO Use kwargs or something, pass whole 'user'
        )

        try:
            new_user.save_to_db()
        except:
            return NoContent, 500

        access_token = create_access_token(identity=user['username'])
        refresh_token = create_refresh_token(identity=user['username'])

        return  {
                   'message': 'User {} successfully created'.format(user['username']),
                    **new_user.as_dict,
                   'access_token': access_token,
                   'refresh_token': refresh_token
               }, 201