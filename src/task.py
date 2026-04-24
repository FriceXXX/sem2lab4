from datetime import datetime
from typing import Protocol, runtime_checkable, List, Dict, Any, Union
from dataclasses import dataclass
from uuid import uuid4
from typing import Optional, Any
from src.validator import (
    ValidatedDescriptor,
    NonDataDescriptor,
    validate_description,
    validate_priority,
    validate_status
)
from src.exceptions import (
    InvalidStateTransitionError,
    TaskAlreadyCompletedError
)

class Task:
    description = ValidatedDescriptor('description', validate_description)
    priority = ValidatedDescriptor('priority', validate_priority, default=3)
    status = ValidatedDescriptor('status', validate_status, default='created')

    def __init__(
            self,
            description: str,
            priority: int = 3,
            status: str = 'created'):
        self._id = str(uuid4())
        self.description = description
        self.priority = priority
        self.status = status
        self._created_at = datetime.now()
        self._completed_at: Optional[datetime] = None
        self._history: list[dict] = []

        self._log_change('created', None, status)

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        raise AttributeError("ID is read-only")

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at

    @property
    def is_active(self) -> bool:
        return self.status in {'created', 'in_progress'}

    @property
    def is_completed(self) -> bool:
        return self.status == 'completed'

    @property
    def age(self) -> float:
        return (datetime.now() - self._created_at).total_seconds() / 3600

    def start(self) -> None:
        if self.status == 'completed':
            raise TaskAlreadyCompletedError(
                f"Нельзя начать выполнение завершённой задачи (ID: {self.id})"
            )

        if self.status == 'in_progress':
            print(f"Задача {self.id} уже в работе")
            return

        old_status = self.status
        self.status = 'in_progress'
        self._log_change('status', old_status, 'in_progress')
        print(f"Задача {self.id} переведена в статус 'в работе'")

    def complete(self) -> None:
        if self.status == 'completed':
            print(f"Задача {self.id} уже завершена")
            return

        if self.status == 'cancelled':
            raise InvalidStateTransitionError(
                f"Нельзя завершить отменённую задачу (ID: {self.id})"
            )

        old_status = self.status
        self.status = 'completed'
        self._completed_at = datetime.now()
        self._log_change('status', old_status, 'completed')
        print(f"Задача {self.id} завершена")

    def cancel(self) -> None:
        if self.status == 'completed':
            raise InvalidStateTransitionError(
                f"Нельзя отменить завершённую задачу (ID: {self.id})"
            )

        if self.status == 'cancelled':
            print(f"Задача {self.id} уже отменена")
            return

        old_status = self.status
        self.status = 'cancelled'
        self._log_change('status', old_status, 'cancelled')
        print(f"Задача {self.id} отменена")

    def update_priority(self, new_priority: int) -> None:
        if self.status == 'completed':
            raise TaskAlreadyCompletedError(
                f"Нельзя изменить приоритет завершённой задачи (ID: {self.id})"
            )

        old_priority = self.priority
        self.priority = new_priority
        self._log_change('priority', old_priority, new_priority)
        print(f"Приоритет задачи {self.id} изменён с {old_priority} на {new_priority}")

    def update_description(self, new_description: str) -> None:
        if self.status == 'completed':
            raise TaskAlreadyCompletedError(
                f"Нельзя изменить описание завершённой задачи (ID: {self.id})"
            )

        old_description = self.description
        self.description = new_description
        self._log_change('description', old_description, new_description)
        print(f"Описание задачи {self.id} обновлено")

    def get_history(self) -> list[dict]:
        return self._history.copy()

    @classmethod
    def create(cls, payload: Any) -> "Task":
        return cls(task_id=str(uuid4()), description=payload)

    def _log_change(self, field: str, old_value: Any, new_value: Any) -> None:
        self._history.append({
            'timestamp': datetime.now(),
            'field': field,
            'old_value': old_value,
            'new_value': new_value
        })

    def __repr__(self) -> str:
        return str({
            'id': self.id,
            'description': self.description,
            'priority': self.priority,
        })

    def __add__(self, other: 'Task') -> 'Task':
        if not  isinstance(other, Task):
            raise TypeError(f"Нельзя добавить Task к {type(other)}")

        description = self.description + "\n" + other.description
        priority = max(self.priority, other.priority)

        return Task(description=description, priority=priority)

    def __radd__(self, other) -> 'Task':
        if other == 0:
            return self
        raise TypeError(f"Нельзя добавить {type(other)} к Task")


@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> List[Task]:
        """
        Get all tasks
        :return: List of Task
        """
        ...