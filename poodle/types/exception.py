class PoodleError(Exception):
    def __init__(self, message):
        super().__init__(message)


class CoreError(PoodleError):
    pass


class CoreConnectionError(CoreError):
    pass


class CoreWSError(CoreError):
    exception: str
    errorcode: str

    def __init__(self, exception, errorcode, message):
        super().__init__(message)
        self.exception = exception
        self.errorcode = errorcode


class CoreAjaxWSError(CoreWSError):
    pass


class AuthError(PoodleError):
    pass


class MissingPrivateAccessKeyError(PoodleError):
    pass


class CourseNotFoundError(PoodleError):
    pass
