from tensorhive.models.UserModel import UserModel


class AllUsers():

    @staticmethod
    def get():
        all_users = list(UserModel.return_all())
        return [user.as_dict for user in all_users], 200
        
