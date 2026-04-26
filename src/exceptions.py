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

class ExecutorError(Exception):
    """Базовое исключение исполнителя задач."""
    pass

class TaskProcessingError(ExecutorError):
    """Ошибка при обработке конкретной задачи."""
    # from src.task import Task
    # def __init__(self, task: Task, cause: Exception):
    #     self.task = task
    #     self.cause = cause
    #     super().__init__(f"[{task.id}] {cause}")

class ExecutorNotStartedError(ExecutorError):
    """Попытка использовать исполнитель до запуска."""
    pass