class AuthException(Exception):
    pass


class UserExistsException(AuthException):
    pass


class UnathorizedException(AuthException):
    pass