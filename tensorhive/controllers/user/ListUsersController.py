from tensorhive.models.user.UserModel import UserModel


class ListUsersController():

    @staticmethod
    def get():
        return [
            user.as_dict for user in UserModel.query.all()
        ], 200
