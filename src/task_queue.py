from typing import List, Iterator, Optional

from src.task_filters import TaskFilter
from .task import Task


class TaskQueue:
    def __init__(self, tasks: Optional[List[Task]] = None):
        self._tasks: List[Task] = []

        if tasks:
            for task in tasks:
                self.add_task(task)

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def add_tasks(self, tasks: List[Task]) -> None:
        for task in tasks:
            self.add_task(task)

    def remove_task(self, task_id: str) -> Optional[Task]:
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                removed = self._tasks.pop(i)
                return removed
        return None

    def filter(self, *filters: TaskFilter) -> Iterator[Task]:
        if not filters:
            yield from self._tasks
            return

        result = self._tasks
        for filter_obj in filters:
            result = filter_obj.apply(result)
            if not result:
                break

        yield from result


    def get_task(self, task_id: str) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def __len__(self) -> int:
        return len(self._tasks)

    def __getitem__(self, index: int) -> Task:
        return self._tasks[index]

    def __iter__(self) -> Iterator[Task]:
        return TaskIterator(self._tasks, self)

    def __repr__(self):
        return f"TaskQueue(tasks={self._tasks[:3]}...)" if len(self._tasks) > 3 else f"TaskQueue(tasks={self._tasks})"

    def status_filter(self, status: str) -> Iterator[Task]:
        for task in self._tasks:
            if task.status == status:
                yield task

    def priority_filter(self, min_priority: int = 1, max_priority: int = 5) -> Iterator[Task]:
        for task in self._tasks:
            if min_priority <= task.priority <= max_priority:
                yield task

    def active_filter(self) -> Iterator[Task]:
        for task in self._tasks:
            if task.is_active:
                yield task

    def completed_filter(self) -> Iterator[Task]:
        for task in self._tasks:
            if task.is_completed:
                yield task

    def avg_priority(self) -> float:
        if not self._tasks:
            return 0.0
        return sum(t.priority for t in self._tasks) / len(self._tasks)

    def clear(self) -> None:
        self._tasks.clear()


class TaskIterator:
    def __init__(self, tasks: List[Task], queue):
        self._tasks = tasks
        self._queue = queue
        self._index = 0

    def __iter__(self) -> 'TaskIterator':
        return self

    def __next__(self) -> Task:
        if self._index >= len(self._tasks):
            raise StopIteration

        task = self._tasks[self._index]
        self._index += 1
        return task

