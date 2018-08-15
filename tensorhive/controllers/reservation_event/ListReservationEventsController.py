from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel


class ListReservationEventsController():

    @staticmethod
    def get(resources_ids, start, end):
        selected_reservation_events = list(ReservationEventModel.return_selected(resources_ids, start, end))
        content = [reservation_event.as_dict for reservation_event in selected_reservation_events]
        return content, 200
