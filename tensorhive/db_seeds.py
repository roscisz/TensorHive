from builtins import len
from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel
from tensorhive.models.user.UserModel import UserModel
import random
from datetime import datetime, timedelta

def init_set(manager):

    gpus_uuids = get_gpu_uuid(manager)

    user_count = 4
    user_count = create_users(user_count)

    now_time = datetime.utcnow()

    start = change_datetime_with_days(now_time,-1*(320 + random.randint(-10,10)))
    end = change_datetime_with_days(start, random.randint(6,18))

    reservation_index_current_position = 1

    #Distribute random events for about half year before and after now
    for _ in range(1, 80):
        time_range = generate_random_time_period(start,end)

        for gpu_uuid in gpus_uuids:
            start = time_range[0]
            end = time_range[1]
            title = 'Reservation no. ' + str(reservation_index_current_position)

            #Reservation on resource with 0.8 chance
            if (random.randint(0,10) <= 8):
                user_random_id = random.randint(0, user_count - 1)
                reservation_index_current_position += 1;
                #Change to random subtime range with 0.3 chance
                if (random.randint(0,10) <= 3):
                    new_time_random_subrange = timeRange = generate_random_time_period(start,end)
                    start = new_time_random_subrange[0]
                    end = new_time_random_subrange[1]

                reservation_event = {'title': title ,
                    'description': '' ,
                    'resourceId': gpu_uuid,
                    'userId': user_random_id,
                    #FORMAT UTC PROPER FORMAT DATES FROM STRING
                    'start': str(start.isoformat())[:23]+'Z',
                    'end': str(end.isoformat())[:23]+'Z'
                    }

                create_reservation_event(reservation_event)

        #Draw lots for gap period or not
        if (random.randint(0, 1) == 1):
            start = change_time(end, timedelta(seconds = random.randint(1, 32)))
        else:
            start = change_datetime_with_days(end, random.randint(2, 8))

        end = change_datetime_with_days(start, random.randint(7, 10))

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

def create_users(users_to_create: int, create_admin=True) -> int:
    '''
    Creates a given amount of users and optionally an admin account,
    then it returns the number of successful operations.
    '''
    created_records = 0
    if create_admin:
        created_records += create_user('admin')

    username_template = 'user_{}'
    usernames = [username_template.format(idx) for idx in range(users_to_create)]
    results = [create_user(username) for username in usernames]
    created_users = sum(results)
    created_records += created_users
    return created_records

def get_gpu_uuid(manager):
    gpus_uuids = []
    for host_data in manager.infrastructure_manager.infrastructure.values():
        if 'GPU' in host_data:
            for gpu in host_data['GPU']:
                gpus_uuids.append(gpu['uuid'])
    return gpus_uuids

def generate_random_time_period(start,end):
    new_start_time = start + (end - start) * random.random()
    end = new_start_time + (end - new_start_time) * random.random()
    return (new_start_time,end)

def change_datetime_with_days(current_time,days):
    return change_time(current_time,timedelta(days = days))

def change_time(current_time,period):
    return current_time + period

#TODO models triggers!
def create_reservation_event(reservation_event):
    def parsed_datetime(input_datetime: str) -> str:
        return datetime.strptime(input_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')

    if not UserModel.find_by_id(reservation_event['userId']):
        return None

    start_time = parsed_datetime(reservation_event['start'])
    end_time = parsed_datetime(reservation_event['end'])
    resource_id = reservation_event['resourceId']
    user_id = reservation_event['userId']

    if (not UserModel.find_by_id(user_id)):
        return None

    if (ReservationEventModel.find_resource_events_between(start_time, end_time, resource_id) is not None):
        return None

    new_reservation_model = ReservationEventModel(
        title=reservation_event['title'],
        description=reservation_event['description'],
        resource_id=resource_id,
        user_id=user_id,
        start=start_time,
        end=end_time
    )

    if not new_reservation_model.save_to_db():
        return None
    return new_reservation_model.as_dict
