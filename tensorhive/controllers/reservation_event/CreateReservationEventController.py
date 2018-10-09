from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from connexion import NoContent
from flask import jsonify


class CreateReservationEventController():

    @staticmethod
    def create(reservation):
        try:
            new_reservation = Reservation(
                title=reservation['title'],
                description=reservation['description'],
                resource_id=reservation['resourceId'],
                user_id=reservation['userId'],
                start=reservation['start'],
                end=reservation['end']
            ).save()
        except AssertionError as e:
            content, status = e, 400
        except IntegrityError:
            content, status = 'Duplicated resource', 409
        except SQLAlchemyError:
            content, status = 'Interal error', 500
        else:
            content, status = new_reservation.as_dict, 201
        finally:
            if isinstance(content, str):
                content = {'msg': content}, status
            return content, status
