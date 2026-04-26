import asyncio
from typing import List, Optional, Callable, Awaitable
from contextlib import asynccontextmanager, AbstractAsyncContextManager

from src.exceptions import TaskProcessingError, ExecutorNotStartedError, ExecutorError
from src.handler import TaskHandler
from src.task import Task
from src.task_queue import TaskQueue

from src.logger import default_logger


class AsyncTaskExecutor:
    def __init__(
            self,
            num_workers: int = 4,
            handler: Optional[TaskHandler] = None,
            max_queue_size: int = 100
    ):
        """Args:
            num_workers: number of worker-coroutines
            max_queue_size: maximum queue size for task-queue
            handler: task-handler instance (PrintHandler by default)
        """
        self._workers = num_workers
        self._queue: asyncio.Queue[Task | None] | None = None
        self._handler = handler
        self._max_queue_size = max_queue_size

        self._worker_tasks: list[asyncio.Task] = []
        self._running = False
        self._logger = default_logger
        self._errors: list[TaskProcessingError] = []

    def set_handler(self, handler: TaskHandler) -> None:
        if not isinstance(handler, TaskHandler):
            raise TypeError(
                f"{handler!r} не реализует TaskHandler: ожидается async def handle(task)"
            )
        self._handler = handler

    async def submit(self, task: Task) -> None:
        """ Submit task to queue
        Raises:
            ExecutorNotStartedError: if executor is already started
        """
        if not self._running or self._queue is None:
            raise ExecutorNotStartedError("Executor not started")
        await self._queue.put(task)
        self._logger.info(f"Submitted task: {task.id}")

    async def submit_batch(self, tasks: List[Task]) -> None:
        """Submit tasks to queue
        Args:
            tasks: List[Task]
        """
        for task in tasks:
            await self.submit(task)
        self._logger.info(f"Tasks submitted: {len(tasks)}")

    @property
    def errors(self) -> list[TaskProcessingError]:
        """errors list"""
        return list(self._errors)

    async def wait_all(self) -> None:
        """Wait for all tasks to complete"""
        if self._queue:
            await self._queue.join()

    async def _worker(self, worker_id: int) -> None:
        """Worker coroutine"""
        self._logger.info(f"Worker {worker_id} started")
        while self._running:
            try:
                task = await self._queue.get()

                if task is None:
                    self._queue.task_done()
                    break

                try:
                    if self._handler is None:
                        self._logger.error(f"<Worker {worker_id}> is not registered")
                        raise ExecutorError("Worker is not registered")

                    await self._handler.handle(task)
                except Exception as e:
                    self._logger.error(f"<Worker {worker_id}>: error {e}")

                finally:
                    self._queue.task_done()

            except asyncio.CancelledError as e:
                self._logger.info(f"Worker {worker_id}: stopped")

            except Exception as e:
                self._logger.error(f"Worker {worker_id}: error {e}")

    async def __aenter__(self) -> "AsyncTaskExecutor":
        self._queue = asyncio.Queue()
        self._running = True
        self._worker_tasks = [
            asyncio.create_task(self._worker(i))
            for i in range(self._workers)
        ]
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        for _ in self._worker_tasks:
            await self._queue.put(None)
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._running = False
        return False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def len_queue(self) -> int:
        return self._queue.qsize() if self._queue else 0

    def __repr__(self) -> str:
        status = "running" if self._running else "stopped"
        return f"AsyncTaskExecutor(status={status}, workers={self._workers}, pending={self.len_queue})"
