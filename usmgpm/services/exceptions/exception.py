import requests


class ServiceError(Exception):
    def __init__(self, response: requests.Response = None, message: str = None):
        self.response = response
        self.message = message

    def __str__(self):
        if self.response is not None:
            return self.response.content.decode()
        elif self.message is not None:
            return self.message
        return 'Unknown Error'


class NotFoundError(ServiceError):
    pass


class InvalidDataError(ServiceError):
    pass


class ForbiddenError(ServiceError):
    pass


class UnauthorizedError(ServiceError):
    pass
