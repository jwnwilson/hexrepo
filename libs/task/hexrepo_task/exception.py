class TaskException(Exception):
    pass


class TaskNotFound(TaskException):
    pass


class DuplicateTaskName(TaskException):
    pass
