from typing import Any, Optional
from datetime import datetime
from src.exceptions import (
    InvalidTaskIdError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusError
)

class NonDataDescriptor:
    def __init__(self, name: str):
        self.name = name

    def __get__(self, obj: Optional[Any], objtype: Optional[type] = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name, None)

class ValidatedDescriptor:
    def __init__(self, name: str, validator: callable, default: Any = None):
        self.name = f"_{name}"
        self.validator = validator
        self.default = default

    def __get__(self, obj: Optional[Any], objtype: Optional[type] = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name, None)

    def __set__(self, obj: Any, value: Any) -> None:
        if value is not None:
            validated_value = self.validator(value)
            obj.__dict__[self.name] = validated_value
        else:
            obj.__dict__[self.name] = value

    def __delete__(self, obj: Any) -> None:
        if self.name in obj.__dict__:
            del obj.__dict__[self.name]


def validate_description(value: str) -> str:
    if not isinstance(value, str):
        raise InvalidDescriptionError(f"Описание должно быть строкой, получен {type(value).__name__}")

    if not value.strip():
        raise InvalidDescriptionError("Описание задачи не может быть пустым")

    if len(value) > 1000:
        raise InvalidDescriptionError(
            f"Описание задачи не может быть длиннее 1000 символов. Получено: {len(value)}"
        )

    return value.strip()

def validate_priority(value: int) -> int:
    if not isinstance(value, int):
        raise InvalidPriorityError(f"Приоритет должен быть целым числом, получен {type(value).__name__}")

    if value < 1 or value > 5:
        raise InvalidPriorityError(
            f"Приоритет должен быть в диапазоне от 1 до 5. Получено: {value}"
        )

    return value

def validate_status(value: str) -> str:
    if not isinstance(value, str):
        raise InvalidStatusError(f"Статус должен быть строкой, получен {type(value).__name__}")

    valid_statuses = {'created', 'in_progress', 'completed', 'cancelled'}
    value_lower = value.lower()
    if value_lower not in valid_statuses:
        raise InvalidStatusError(
            f"Недопустимый статус: {value}. Допустимые статусы: {', '.join(valid_statuses)}"
        )

    return value_lower


