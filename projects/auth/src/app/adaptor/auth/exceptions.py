class AuthException(Exception):
    pass


class UserExistsException(AuthException):
    pass


class InvalidPasswordException(AuthException):
    pass


class InvalidVerificationCodeException(AuthException):
    pass

class UnathorizedException(AuthException):
    pass