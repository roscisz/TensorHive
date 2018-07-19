import datetime

from connexion import NoContent
from tensorhive.controllers.user.UserRegistration import UserRegistration
from tensorhive.controllers.user.AllUsers import AllUsers


def post(user):
    '''Create new user'''
    return UserRegistration.register(user)

def search():
    '''Get all users'''
    return AllUsers.get()

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
