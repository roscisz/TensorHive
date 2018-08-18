from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController


def init_set():
    userList = [ {'username': 'Kamil Nowodworski'},
                 {'username': 'Tomasz Berezowski'},
                 {'username': 'Kamil Grinholc'},
                 {'username': 'Artur Poliński'},
                 {'username': 'Grzegorz Chlodzinski'}
    ]
    for user in userList:
        CreateUserController.register(user)

