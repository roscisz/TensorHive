from tensorhive.models.User import User


class ListUsersController():

    @staticmethod
    def get():
        return [
            user.as_dict for user in User.all()
        ], 200
