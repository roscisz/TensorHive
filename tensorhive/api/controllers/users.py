import datetime

from flask_jwt_extended import jwt_required
from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.user.ListUsersController import ListUsersController

#TODO others controllers
@jwt_required
def search():
    '''Get all users'''
    return ListUsersController.get()
