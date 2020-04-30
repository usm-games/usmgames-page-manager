
class ServiceError(Exception):
    pass


class NotFoundError(ServiceError):
    pass


class InvalidDataError(ServiceError):
    pass


class ForbiddenError(ServiceError):
    pass


class UnauthorizedError(ServiceError):
    pass
