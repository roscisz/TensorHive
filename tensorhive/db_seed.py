from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController
import random


def init_set():
    gpu_dict = {}
    for x in range(0, 4):
        gpu_dict['GPU'+str(x)] = "GPU" + str(random.choice("0123456789ABCDEF", k=8)) + "-" + str(
            random.choice("0123456789ABCDEF", k=4)) + "-" + str(random.choice("0123456789ABCDEF", k=4)) + "-" + str(
            random.choice("0123456789ABCDEF", k=4)) + "-" + str(random.choice("0123456789ABCDEF", k=12))