from tensorhive.models.ReservationEventModel import ReservationEventModel


class AllReservationEvents():

    @staticmethod
    def get():
        all_reservation_events = list(ReservationEventModel.return_all())
        content = [reservation_event.as_dict for reservation_event in all_reservation_events]
        return content, 200
