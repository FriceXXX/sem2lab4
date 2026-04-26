import asyncio

from typing import List, Iterator, Optional

from src.task_filters import TaskFilter
from .task import Task
from src.logger import default_logger as logger


class TaskQueue:
    def __init__(self, tasks: Optional[List[Task]] = None, maxsize: int = 0):
        self._tasks: List[Task] = []
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self._logger = logger
        self.is_stopped = False

        if tasks:
            for task in tasks:
                self.put_nowait(task)

    async def put(self, task: Task):
        await self._queue.put(task)
        self._tasks.append(task)
        self._logger.debug(f"put {task.id} async. size = {self.qsize()}")

    def put_nowait(self, task: Task):
        self._tasks.append(task)
        self._queue.put_nowait(task)
        self._logger.debug(f"put {task.id} nowait. size = {self.qsize()}")


    async def put_tasks(self, tasks: List[Task]) -> None:
        for task in tasks:
            await self._queue.put(task)
            self._tasks.append(task)
            self._logger.debug(f"put {task.id} async. size = {self.qsize()}")

    async def get(self) -> Task:
        if self.is_stopped:
            raise ValueError("Task queue is stopped")
        if self.empty():
            raise asyncio.QueueEmpty("Task queue is empty")

        task = await self._queue.get()
        self._logger.debug(f"get {task.id} async. size = {self.qsize()}")
        return task

    def get_nowait(self) -> Task:
        task = self._queue.get_nowait()
        self._logger.debug(f"get {task.id} nowait. size = {self.qsize()}")
        return task

    def remove_task(self, task_id: str) -> Optional[Task]:
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                removed = self._tasks.pop(i)
                self._logger.info(f"remove {removed.id}. size = {self.qsize()}")
                return removed
        return None

    def clear(self) -> None:
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break

        self._tasks.clear()
        self._logger.info(f"queue {self._queue.qsize()} cleared. size = {self.qsize()}")

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

    def full(self) -> bool:
        return self._queue.full()

    def empty(self) -> bool:
        return self._queue.empty()

    def qsize(self) -> int:
        return self._queue.qsize()

    async def stop(self) -> None:
        self.is_stopped = True
        self._logger.info("queue is stopped")

    def is_stopped(self) -> bool:
        return self.is_stopped

    async def join(self) -> None:
        await self._queue.join()
        self._logger.info("All tasks done")

    def task_done(self) -> None:
        self._queue.task_done()

    async def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            if self.is_stopped or self.empty():
                raise StopAsyncIteration
            return await self.get()
        except asyncio.QueueEmpty:
            raise StopAsyncIteration

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

