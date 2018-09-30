from tensorhive.models.user.UserModel import UserModel
from tensorhive.models.role.RoleModel import RoleModel
from connexion import NoContent
from flask_jwt_extended import create_access_token, create_refresh_token

class CreateUserController():
    # TODO Add more user parameters

    @staticmethod
    def register(user):
        if UserModel.find_by_username(user['username']):
            # Duplicated resource
            return NoContent, 409

        new_user = UserModel(
            username = user['username'],
            password = UserModel.generate_hash(user['password'])
        )

        try:
            new_user.save_to_db()
            new_role = RoleModel(
                name='user',
                user_id=new_user.id
            )
            try:
                new_role.save_to_db()
            except:
                return NoContent, 500
        except:
            return NoContent, 500


        access_token = create_access_token(identity=user['username'])
        refresh_token = create_refresh_token(identity=user['username'])

        return  {
            'msg': 'User {} successfully created'.format(user['username']), **new_user.as_dict,
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201