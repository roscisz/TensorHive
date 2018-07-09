import datetime

from connexion import NoContent
#from tensorhive.core_anew.models.UserModel import UserModel

#TODO replace with database model
users = {}

def post(user):
    '''Create new user'''
    count = len(users)
    user['id'] = count + 1
    user['registered'] = datetime.datetime.now()
    users[user['id']] = user
    return user, 201

# all users
def search():
    '''Get all users'''
    return list(users.values())

# TODO implement
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
