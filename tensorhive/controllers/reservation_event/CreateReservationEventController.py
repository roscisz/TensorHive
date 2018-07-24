from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel
from tensorhive.models.user.UserModel import UserModel
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
        if not UserModel.find_by_id(reservation_event['userId']):
            return NoContent, 500

        start_time = parsed_datetime(reservation_event['start'])
        end_time = parsed_datetime(reservation_event['end'])
        node_id = reservation_event['nodeId']
        user_id = reservation_event['userId']

        if (not UserModel.find_by_id(user_id)):
            return NoContent, 500

        if (ReservationEventModel.find_node_events_between(start_time, end_time, node_id) is not None):
            return NoContent, 500

        new_reservation_model = ReservationEventModel(
            title=reservation_event['title'],
            description=reservation_event['description'],
            node_id=node_id,
            user_id=user_id,
            start=start_time,
            end=end_time
        )

        if not new_reservation_model.save_to_db():
            return NoContent, 500
        return new_reservation_model.as_dict, 201
