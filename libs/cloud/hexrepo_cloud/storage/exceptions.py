class StorageException(Exception):
    pass


class StorageAlreadyExists(StorageException):
    pass


class StorageInvalid(StorageException):
    pass
