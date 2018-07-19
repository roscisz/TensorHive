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

# TODO Implement (see API specification)
# def put(id, user):
#     id = int(id)
#     if pets.get(id) is None:
#         return NoContent, 404
#     pets[id] = pet

#     return pets[id]


# def delete(id):
#     id = int(id)
#     if pets.get(id) is None:
#         return NoContent, 404
#     del pets[id]
#     return NoContent, 204


# def get(id):
#     id = int(id)
#     if pets.get(id) is None:
#         return NoContent, 404

#     return pets[id]
