class SillyException(Exception):
    pass


class SillyAccessError(SillyException):
    pass


class SillyUserError(SillyException):
    pass


class SillyValidationError(SillyUserError):
    pass
