from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController
import random


def init_set():
    gpu_dict = {}

    for x in range(0, 4):
        gpu_dict['GPU' + str(x)] = "GPU" + str(random.choices("0123456789ABCDEF", k=8)) + "-" + str(
            random.choices("0123456789ABCDEF", k=4)) + "-" + str(random.choices("0123456789ABCDEF", k=4)) + "-" + str(
            random.choices("0123456789ABCDEF", k=4)) + "-" + str(random.choices("0123456789ABCDEF", k=12))

    user_list = [{'username': 'admin'}
    ]

    CreateUserController.register(user_list[0])
    user_count = 4

    for x in range(1, user_count):
        user_list.append({'username': 'user' + str(x)})
        CreateUserController.register(user_list[x])
