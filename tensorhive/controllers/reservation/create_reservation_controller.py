from tensorhive.models.Reservation import Reservation
from flask_jwt_extended import jwt_required
from tensorhive.database import flask_app


@jwt_required
def create(reservation):
    try:
        with flask_app.app_context():
            new_reservation = Reservation(
                title=reservation['title'],
                description=reservation['description'],
                protected_resource_id=reservation['resourceId'],
                user_id=reservation['userId'],
                starts_at=reservation['start'],
                ends_at=reservation['end']
            )
            new_reservation.save()
    except AssertionError as e:
        content, status = {'msg': e}, 400
    except Exception as e:
        content, status = {'msg': e}, 500
    else:
        # TODO Include additional message
        content, status = {'reservation': new_reservation.as_dict}, 201
    finally:
        return content, status
