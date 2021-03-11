class ForbiddenException(Exception):
    def __init__(self, message='Action forbidden'):
        super().__init__(message)
        self.message = message
