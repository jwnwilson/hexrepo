class RepositoryException(Exception):
    pass


class MissingRequiredFiltered(RepositoryException):
    pass


class SessionNotInitialised(RepositoryException):
    pass


class RecordNotFound(RepositoryException):
    pass


class DuplicateRecord(RepositoryException):
    pass


class IntegrityError(RepositoryException):
    pass


class InvalidArgument(RepositoryException):
    pass
