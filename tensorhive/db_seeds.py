from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController
import random
from datetime import datetime, timedelta


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

    now_time = datetime.utcnow()
    start = now_time - timedelta(days=150 + random.randint(-10,10))
    end = start + timedelta(days=random.randint(2,18))

    z = 1;

    for x in range(1, 150):
        start = start + (end - start) * random.random()
        end = start + (end - start) * random.random()
        user_random_id = random.randint(0,user_count-1)
        random_date = start + (end - start) * random.random()

        title = 'Reservation no. ' + str(z)
        old_user_random_id = 0
        old_title = ''
        for y in range(0, 3):
            if (random.randint(0, 1) == 1):
                if (random.randint(0,3) < 1):
                    old_user_random_id = user_random_id
                    user_random_id = random.randint(0, user_count - 1)
                    start = datetime.now() - timedelta(days=150)
                    old_title = title
                    z+=1;
                    title = 'Reservation no. ' + str(z)

                reservation_event = {'title': title ,
                    'description': '' ,
                    'resourceId': gpu_dict['GPU'+str(y)],
                    'userId': user_random_id,
                    'start': str(start.isoformat())[:23]+'Z',
                    'end': str(end.isoformat())[:23]+'Z'
                    }

                user_random_id = old_user_random_id
                title = old_title
                CreateReservationEventController.create(reservation_event)

        if (random.randint(0, 1) == 1):
            start = end + timedelta(seconds = random.randint(1, 32))
        else:
            start = end + timedelta(days=random.randint(2, 8))

        end = start + timedelta(days=random.randint(2, 18))

