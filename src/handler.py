import asyncio
import time
from typing import Protocol, runtime_checkable, Optional
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from src.task import Task
from src.logger import default_logger as logger



@runtime_checkable
class TaskHandler(Protocol):
    """
    Контракт для обработчика задач
    """

    async def handle(self, task: Task) -> None:
        """
        Args:
            task: Задача для обработки
        """
        ...

    @property
    def name(self) -> str:
        """Имя обработчика"""
        ...

class BaseHandler(ABC):
    def __init__(self, name: Optional[str] = None):
        self._name = name or self.__class__.__name__
        self._logger = logger

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    async def handle(self, task: Task) -> None:
        pass

    @asynccontextmanager
    async def process(self, task: Task) -> None:
        start_time = time.time()
        self._logger.info(f"[{self._name}] Handling {task.id}")

        try:
            yield
            elapsed_time = time.time() - start_time
            self._logger.info(f"[{self._name}] {task.id}: Elapsed time: {elapsed_time}")
        except Exception as e:
            elapsed_time = time.time() - start_time
            self._logger.error(f"[{self._name}] {task.id}: Exception: {e}. Elapsed time: {elapsed_time}")
            raise

        def __repr__(self) -> str:
            return f"{self._name}"

class PrintHandler(BaseHandler):
    """default handler"""
    async def handle(self, task: Task) -> None:
        async with self.process(task):
            await asyncio.sleep(1)
            print(f"[{self._name}] Handled {task.id} - {task.description}")
            print(f" Priority: {task.priority}, Status: {task.status}")


class ErrorHandler:
    async def handle(self, task: Task) -> None:
        if task.priority > 5:
            raise ValueError(f"Priority is too high: {task.priority} > 5")
        await asyncio.sleep(0.05)
        print(f"{task.id} handled")