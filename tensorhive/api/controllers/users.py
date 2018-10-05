from tensorhive.authorization import admin_required
from tensorhive.controllers.user.ListUsersController import ListUsersController

#TODO others controllers
@admin_required
def search():
    '''Get all users'''
    return ListUsersController.get()
