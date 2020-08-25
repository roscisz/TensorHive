class InvalidRequestException(Exception):
    """Exception thrown by DB models when requested operation would be impossible/incorrect"""

    def __init__(self, message='The request was invalid'):
        super().__init__(message)
        self.message = message
