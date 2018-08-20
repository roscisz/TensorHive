import datetime

from connexion import NoContent
from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.user.ListUsersController import ListUsersController


def post(user):
    '''Create new user'''
    return CreateUserController.register(user)

def search():
    '''Get all users'''
    return ListUsersController.get()
