from tensorhive.models.user.UserModel import UserModel
from connexion import NoContent
from flask import jsonify


class UserRegistration():
    # TODO Add authentication, uniqueness checks
    # TODO Add more user parameters

    @staticmethod
    def register(user):
        if UserModel.find_by_username(user['username']):
            # Duplicated resource
            return NoContent, 409

        new_user = UserModel(
            username=user['username']
            # TODO Use kwargs or something, pass whole 'user'
        )

        try:
            new_user.save_to_db()
        except:
            return NoContent, 500
        return new_user.as_dict, 201