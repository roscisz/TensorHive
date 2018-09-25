import datetime

from flask_jwt_extended import jwt_required,jwt_refresh_token_required
from tensorhive.controllers.user.UserLoginController import LoginUserController
from tensorhive.controllers.user.UserLogoutController import LogoutUserController
from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.user.CreateRefreshedUserTokenController import CreateRefreshedUserTokenController


def post_login(user):
    '''Login user'''
    return LoginUserController.login(user)

@jwt_refresh_token_required
def get_refreshed_access_token():
    '''Refresh user token'''
    return CreateRefreshedUserTokenController.create()

@jwt_required
def post_logout_access_token():
    '''Revoking the current users access token'''
    return LogoutUserController.delete_logout('Access')

@jwt_refresh_token_required
def post_logout_refresh_token():
    '''Revoking the refresh users access token'''
    return LogoutUserController.delete_logout('Refresh')

def post_register(user):
    '''Create new user'''
    return CreateUserController.register(user)
