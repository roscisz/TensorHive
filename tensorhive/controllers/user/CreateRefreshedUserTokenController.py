from flask_jwt_extended import create_access_token, get_jwt_identity


class CreateRefreshedUserTokenController():

    @staticmethod
    def create():
        try:
            current_user = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user)
            return {
                'msg': 'Refreshed token',
                'access_token': new_access_token
            }, 201
        except:
            return {
                'msg': '{} token has not been revoked due to error'.format(type)
            }, 501
