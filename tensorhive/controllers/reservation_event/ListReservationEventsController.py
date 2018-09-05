from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel


class ListReservationEventsController():
    @staticmethod
    def all():
        reservations = list(ReservationEventModel.return_all())
        content = [reservation.as_dict for reservation in reservations]
        return content, 200

    @staticmethod
    def get(resources_ids, start, end):
        # All args are required at once, otherwise return 400
        all_not_none = resources_ids and start and end
        if all_not_none:
            reservations = list(ReservationEventModel.filter_by_uuids_and_time_range(
                resources_ids, start, end))
            content = [reservation.as_dict for reservation in reservations]
            return content, 200
        else:
            return 'Bad request', 400
