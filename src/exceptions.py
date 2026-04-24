class TaskError(Exception):
    pass

class InvalidTaskIdError(TaskError):
    """Исключение при некорректном идентификаторе задачи"""
    pass

class InvalidDescriptionError(TaskError):
    """Исключение при некорректном описании задачи"""
    pass

class InvalidPriorityError(TaskError):
    """Исключение при некорректном приоритете задачи"""
    pass

class InvalidStatusError(TaskError):
    """Исключение при некорректном статусе задачи"""
    pass

class InvalidStateTransitionError(TaskError):
    """Исключение при некорректном переходе состояния"""
    pass

class TaskAlreadyCompletedError(TaskError):
    """Исключение при попытке изменить завершённую задачу"""
    pass