from tensorhive.models.Reservation import Reservation


class ListReservationEventsController():
    @staticmethod
    def all():
        return [
            reservation.as_dict for reservation in Reservation.query.all()
        ], 200

    @staticmethod
    def get(resources_ids, start, end):

        # All args are required at once, otherwise return 400
        all_not_none = resources_ids and start and end
        if all_not_none:
            reservations = list(Reservation.filter_by_uuids_and_time_range(
                resources_ids, start, end))
            content = [reservation.as_dict for reservation in reservations]
            return content, 200
        else:
            return 'Bad request', 400
