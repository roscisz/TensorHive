class ForbiddenReservationException(Exception):
    def __init__(self, message='Reservation forbidden'):
        super().__init__(message)
        self.message = message
