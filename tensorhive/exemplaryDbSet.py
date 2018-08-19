from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController


def init_set():
    gpu = ['GPU1','GPU2','GPU3','GPU4']

    userList = [ {'username': 'Kamil Nowodworski'},
                 {'username': 'Tomasz Berezowski'},
                 {'username': 'Kamil Grinholc'},
                 {'username': 'Artur Poliński'},
                 {'username': 'Grzegorz Chlodzinski'},
                 {'username': 'Kamil Nowodworski'}
    ]
    for user in userList:
        CreateUserController.register(user)

    reservationEventsList = [{'title': 'attention_ocr + scheduled_sampling' ,
                'description': '' ,
                'resourceId': gpu.count('GPU4'),
                'userId': userList.count({'username': 'Kamil Nowodworski'}),
                'start': '2018-03-16T00:00:00.000Z',
                'end': '2018-03-18T23:59:59.999Z'
                },
    ]

    for reservationEvent in reservationEventsList:
        CreateReservationEventController.create(reservationEvent)