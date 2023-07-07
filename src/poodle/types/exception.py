class PoodleError(Exception):
    def __init__(self, message):
        super().__init__(message)


class CoreError(PoodleError):
    def __init__(self, message):
        super().__init__(message)


class CoreConnectionError(CoreError):
    def __init__(self, message):
        super().__init__(message)


class CoreWSError(CoreError):
    exception: str
    errorcode: str

    def __init__(self, exception, errorcode, message):
        super().__init__(message)
        self.exception = exception
        self.errorcode = errorcode
