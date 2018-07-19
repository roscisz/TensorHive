from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel
from connexion import NoContent
from flask import jsonify
from datetime import datetime


class CreateReservationEventController():

    @staticmethod
    def create(reservation_event):
        def parsed_datetime(input_datetime: str) -> str:
            try:
                return datetime.strptime(input_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                return datetime.strptime(input_datetime, '%Y-%m-%dT%H:%M:%S')

        new_reservation_model = ReservationEventModel(
            title=reservation_event['title'],
            description=reservation_event['description'],
            start_datetime=parsed_datetime(reservation_event['start_datetime']),
            end_datetime=parsed_datetime(reservation_event['end_datetime'])
        )

        if not new_reservation_model.save_to_db():
            return NoContent, 500
        return new_reservation_model.as_dict, 201
