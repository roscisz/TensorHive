from tensorhive.authorization import admin_required
from tensorhive.controllers.user.ListUsersController import ListUsersController


@admin_required
def search():
    '''Get all users'''
    return ListUsersController.get()
