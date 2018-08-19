from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController


def init_set():
    gpu = ['GPU0','GPU1','GPU2','GPU3','GPU4']

    userList = [ {'username': 'Kamil Nowodworski'},
                 {'username': 'Tomasz Berezowski'},
                 {'username': 'Kamil Grinholc'},
                 {'username': 'Artur Poliński'},
                 {'username': 'Grzegorz Chlodzinski'},
                 {'username': 'Kamil Szymański'},
                 {'username': 'Paweł Rościszewski'},
                 {'username': 'Jacek Rumiński'}
    ]
    for user in userList:
        CreateUserController.register(user)

    reservationEventsList = [{'title': 'Attention_ocr + scheduled_sampling' ,
                'description': '' ,
                'resourceId': gpu.count('GPU4')+1,
                'userId': userList.count({'username': 'Kamil Nowodworski'})+1,
                'start': '2018-03-16T00:00:00.000Z',
                'end': '2018-03-18T23:59:59.999Z'
                },
                {'title': 'Attention_ocr' ,
                'description': '' ,
                'resourceId': gpu.count('GPU3')+1,
                'userId': userList.count({'username': 'Kamil Nowodworski'})+1,
                'start': '2018-05-10T00:00:00.000Z',
                'end': '2018-05-10T23:59:59.999Z'
                },
                {'title': 'PointNet' ,
                'description': '' ,
                'resourceId': gpu.count('GPU1')+1,
                'userId': userList.count({'username': 'Kamil Szymański'})+1,
                'start': '2018-05-11T00:00:00.000Z',
                'end': '2018-05-12T23:59:59.999Z'
                },
                {'title': 'DeepRL i DM Lab' ,
                'description': 'Part 1' ,
                'resourceId': gpu.count('GPU3')+1,
                'userId': userList.count({'username': 'Grzegorz Chlodzinski'})+1,
                'start': '2018-05-23T00:00:00.000Z',
                'end': '2018-05-30T23:59:59.999Z'
                },
                {'title': 'DeepRL i DM Lab' ,
                'description': 'Part 2' ,
                'resourceId': gpu.count('GPU0')+1,
                'userId': userList.count({'username': 'Grzegorz Chlodzinski'})+1,
                'start': '2018-05-23T00:00:00.000Z',
                'end': '2018-05-30T23:59:59.999Z'
                },
                {'title': 'DeepRL i DM Lab' ,
                'description': 'Part 2' ,
                'resourceId': gpu.count('GPU1')+1,
                'userId': userList.count({'username': 'Grzegorz Chlodzinski'})+1,
                'start': '2018-05-23T00:00:00.000Z',
                'end': '2018-05-30T23:59:59.999Z'
                },
                {'title': 'DeepRL i DM Lab' ,
                'description': 'Part 3' ,
                'resourceId': gpu.count('GPU0')+1,
                'userId': userList.count({'username': 'Grzegorz Chlodzinski'})+1,
                'start': '2018-05-31T00:00:00.000Z',
                'end': '2018-06-03T23:59:59.999Z'
                },
                {'title': 'DeepRL i DM Lab' ,
                'description': 'Part 3' ,
                'resourceId': gpu.count('GPU1')+1,
                'userId': userList.count({'username': 'Grzegorz Chlodzinski'})+1,
                'start': '2018-05-31T00:00:00.000Z',
                'end': '2018-06-03T23:59:59.999Z'
                },
                {'title': 'Prezentacja dla koła Gradient, distributed GAN' ,
                'description': '' ,
                'resourceId': gpu.count('GPU4')+1,
                'userId': userList.count({'username': 'Paweł Rościszewski'})+1,
                'start': '2018-06-05T00:00:00.000Z',
                'end': '2018-06-06T23:59:59.999Z'
                },
                {'title': 'attention_ocr+bidirectional_lstm+sigmoidal_sampling' ,
                'description': '' ,
                'resourceId': gpu.count('GPU0')+1,
                'userId': userList.count({'username': 'Kamil Nowodworski'})+1,
                'start': '2018-06-05T00:00:00.000Z',
                'end': '2018-06-06T23:59:59.999Z'
                },
                {'title': 'attention_ocr+bidirectional_lstm+sigmoidal_sampling' ,
                'description': '' ,
                'resourceId': gpu.count('GPU1')+1,
                'userId': userList.count({'username': 'Kamil Nowodworski'})+1,
                'start': '2018-06-05T00:00:00.000Z',
                'end': '2018-06-06T23:59:59.999Z'
                },
                {'title': 'Modyfikacja Mobile Net' ,
                'description': '' ,
                'resourceId': gpu.count('GPU2')+1,
                'userId': userList.count({'username': 'Kamil Grinholc'})+1,
                'start': '2018-06-10T00:00:00.000Z',
                'end': '2018-06-12T23:59:59.999Z'
                },
                {'title': 'Modyfikacja Mobile Net' ,
                'description': '' ,
                'resourceId': gpu.count('GPU3')+1,
                'userId': userList.count({'username': 'Kamil Grinholc'})+1,
                'start': '2018-06-10T00:00:00.000Z',
                'end': '2018-06-12T23:59:59.999Z'
                },
                {'title': 'Szkola letnia' ,
                'description': 'SERWER ZAREZEROWANY DLA PRAC ZWIĄZANYCH ZE SZKOŁĄ LETNIA!!!' ,
                'resourceId': gpu.count('GPU0')+1,
                'userId': userList.count({'username': 'Jacek Rumiński'})+1,
                'start': '2018-06-20T00:00:00.000Z',
                'end': '2018-07-07T23:59:59.999Z'
                },
                {'title': 'Szkola letnia' ,
                'description': 'SERWER ZAREZEROWANY DLA PRAC ZWIĄZANYCH ZE SZKOŁĄ LETNIA!!!' ,
                'resourceId': gpu.count('GPU1')+1,
                'userId': userList.count({'username': 'Jacek Rumiński'})+1,
                'start': '2018-06-20T00:00:00.000Z',
                'end': '2018-07-07T23:59:59.999Z'
                },
                {'title': 'Szkola letnia' ,
                'description': 'SERWER ZAREZEROWANY DLA PRAC ZWIĄZANYCH ZE SZKOŁĄ LETNIA!!!' ,
                'resourceId': gpu.count('GPU2')+1,
                'userId': userList.count({'username': 'Jacek Rumiński'})+1,
                'start': '2018-06-20T00:00:00.000Z',
                'end': '2018-07-07T23:59:59.999Z'
                },
                {'title': 'Szkola letnia' ,
                'description': 'SERWER ZAREZEROWANY DLA PRAC ZWIĄZANYCH ZE SZKOŁĄ LETNIA!!!' ,
                'resourceId': gpu.count('GPU3')+1,
                'userId': userList.count({'username': 'Jacek Rumiński'})+1,
                'start': '2018-06-20T00:00:00.000Z',
                'end': '2018-07-07T23:59:59.999Z'
                },
                {'title': 'Szkola letnia' ,
                'description': 'SERWER ZAREZEROWANY DLA PRAC ZWIĄZANYCH ZE SZKOŁĄ LETNIA!!!' ,
                'resourceId': gpu.count('GPU4')+1,
                'userId': userList.count({'username': 'Jacek Rumiński'})+1,
                'start': '2018-06-20T00:00:00.000Z',
                'end': '2018-07-07T23:59:59.999Z'
                }
    ]

    for reservationEvent in reservationEventsList:
        CreateReservationEventController.create(reservationEvent)