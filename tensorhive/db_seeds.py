from builtins import len

from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController
from tensorhive.models.user.UserModel import UserModel
import random
from datetime import datetime, timedelta


def init_set(manager):

    gpu_dict = get_gpu_uuid(manager)

    user_count = 4
    user_count = create_users(user_count)

    now_time = datetime.utcnow()

    start = change_datetime_with_days(now_time,-1*(150 + random.randint(-10,10)))
    end = change_datetime_with_days(start, random.randint(6,18))

    index_current_counter = 1;

    for x in range(1, 150):
        timeRange = generate_random_time_period(start,end)
        start = timeRange[0]
        end = timeRange[1]

        user_random_id = random.randint(0,user_count-1)
        random_date = generate_random_time_period(start,end)

        title = 'Reservation no. ' + str(index_current_counter)
        old_user_random_id = 0
        old_title = ''
        for gpuIndex in range(0, len(gpu_dict)):
            if (random.randint(0, 1) == 1):
                if (random.randint(0,3) < 1):
                    old_user_random_id = user_random_id
                    user_random_id = random.randint(0, user_count - 1)
                    start = datetime.now() - timedelta(days=150)
                    old_title = title
                    index_current_counter+=1;
                    title = 'Reservation no. ' + str(index_current_counter)

                reservation_event = {'title': title ,
                    'description': '' ,
                    'resourceId': gpu_dict['GPU'+str(gpuIndex)],
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

def create_user(username):
    if UserModel.find_by_username(username):
        return 1

    new_user = UserModel(
        username=username
    )
    try:
        new_user.save_to_db()
    except:
        return 0
    return 1

def create_users(user_count):
    made_users_count = 0
    user_list = ['admin'
                ]

    made_users_count += create_user(user_list[0])

    for x in range(1, user_count):
        user_list.append('user' + str(x))
        made_users_count += create_user(user_list[x])

    return made_users_count

def get_gpu_uuid(manager):
    gpu_dict = {}
    gpu_index = 0
    for host_data in manager.infrastructure_manager.infrastructure.values():
        if 'GPU' in host_data:
            for gpu in host_data['GPU']:
                gpu_dict['GPU{}'.format(gpu_index)] = gpu['uuid']
                gpu_index += 1
    return gpu_dict

def generate_random_time_period(start,end):
    start = start + (end - start) * random.random()
    end = start + (end - start) * random.random()
    return (start,end)

def change_datetime_with_days(current_time,days):
    return change_time(current_time,timedelta(days = days))

def change_time(current_time,period):
    return current_time + period
