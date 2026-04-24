from abc import ABC, abstractmethod
from typing import List, Iterator, Callable

from src.task import Task


class TaskFilter(ABC):
    @abstractmethod
    def apply(self, task: Task) -> Task:
        pass


class StatusFilter(TaskFilter):
    def __init__(self, status: str):
        self.status = status

    def apply(self, tasks: List[Task]) -> Iterator[Task]:
        for task in tasks:
            if task.status == self.status:
                yield task

class PriorityFilter(TaskFilter):
    def __init__(self, min_priority: int = 1, max_priority: int = 5):
        self.min_priority = min_priority
        self.max_priority = max_priority

    def apply(self, tasks: List[Task]) -> Iterator[Task]:
        for task in tasks:
            if self.min_priority <= task.priority <= self.max_priority:
                yield task

class ActiveFilter(TaskFilter):
    def apply(self, tasks: List[Task]) -> Iterator[Task]:
        for task in tasks:
            if task.is_active:
                yield task

class CompletedFilter(TaskFilter):
    def apply(self, tasks: List[Task]) -> Iterator[Task]:
        for task in tasks:
            if task.is_completed:
                yield task

class ANDFilter(TaskFilter):
    def __init__(self, *filters: TaskFilter):
        self.filters = filters

    def apply(self, tasks: List[Task]) -> Iterator[Task]:
        result = tasks
        for filter in self.filters:
            result = list(filter.apply(result))
            if not result:
                break
        yield from result

class ORFilter(TaskFilter):
    def __init__(self, *filters: TaskFilter):
        self.filters = filters

    def apply(self, tasks: List[Task]) -> Iterator[Task]:
        seen_ids = set()
        for filter in self.filters:
            for task in filter.apply(tasks):
                if task.id not in seen_ids:
                    seen_ids.add(task.id)
                    yield task

class NOTFilter(TaskFilter):
    pass


class CustomFilter(TaskFilter):
    def __init__(self, predicate: Callable[[Task], bool]):
        self.predicate = predicate

    def apply(self, tasks: List[Task]) -> Iterator[Task]:
        for task in tasks:
            if self.predicate(task):
                yield task