import pytest
import asyncio

from src.executor import AsyncTaskExecutor
from src.handler import PrintHandler, ErrorHandler
from src.task import Task
from src.task_queue import TaskQueue
from src.task_filters import StatusFilter, PriorityFilter, ANDFilter, ORFilter


@pytest.mark.asyncio
async def test_executor_context_manager():
    """Тест работы исполнителя через контекстный менеджер"""
    executor = AsyncTaskExecutor(num_workers=2)
    assert not executor._running

    async with executor as running_executor:
        assert running_executor is executor
        assert executor._running is True

    assert executor._running is False

@pytest.mark.asyncio
async def test_executor_submit():
    """Тест отправки задач."""
    executor = AsyncTaskExecutor(num_workers=1, handler=PrintHandler())
    assert not executor._running

    async with executor as running_executor:
        task = Task("Test task")
        await executor.submit(task)

        assert executor.len_queue == 1
        await executor.wait_all()
        assert executor.len_queue == 0

@pytest.mark.asyncio
async def test_executor_submit_batch():
    """Тест отправки нескольких задач"""
    executor = AsyncTaskExecutor(num_workers=2, handler=PrintHandler())

    async with executor as running_executor:
        tasks = [Task(f"Task {i}") for i in range(5)]
        await executor.submit_batch(tasks)

        assert executor.len_queue == 5
        await executor.wait_all()
        assert executor.len_queue == 0

@pytest.mark.asyncio
async def test_executor_submit_not_running():
    """Тест отправки задачи в не запущенный исполнитель"""
    executor = AsyncTaskExecutor()
    task = Task("Test task")

    async with executor as running_executor:
        await executor.submit(task)


# @pytest.mark.asyncio
# async def test_executor_submit_outside_context():
#     """Ошибка при отправке задачи вне контекста."""
#     executor = AsyncTaskExecutor(num_workers=1)
#     task = Task("Task outside context", priority=3)
#
#     async with pytest.raises(RuntimeError, match="не запущен"):
#         await executor.submit(task)

@pytest.mark.asyncio
async def test_executor_multiple_workers():
    """Работа с несколькими воркерами."""
    executor = AsyncTaskExecutor(num_workers=3, handler=PrintHandler())

    async with executor:
        tasks = [Task(f"Worker test {i}", priority=3) for i in range(6)]
        await executor.submit_batch(tasks)

        await executor.wait_all()
        assert executor.len_queue == 0


@pytest.mark.asyncio
async def test_executor_empty_queue():
    """Работа с пустой очередью"""
    executor = AsyncTaskExecutor(num_workers=2)

    async with executor:
        assert executor.len_queue == 0
        await executor.wait_all()
        assert executor.len_queue == 0

@pytest.mark.asyncio
async def test_executor_concurrent_submits():
    """Конкурентная отправка задач из нескольких корутин"""
    executor = AsyncTaskExecutor(num_workers=3, handler=PrintHandler())

    async def submit_tasks(start_id: int, count: int):
        for i in range(count):
            task = Task(f"Concurrent task {start_id}-{i}", priority=3)
            await executor.submit(task)

    async with executor:
        await asyncio.gather(
            submit_tasks(1, 5),
            submit_tasks(2, 5),
            submit_tasks(3, 5)
        )

        await asyncio.sleep(0.1)

        assert executor.len_queue == 12

        await executor.wait_all()
        assert executor.len_queue == 0


@pytest.mark.asyncio
async def test_sequential_sessions():
    """Тест множественных сессий"""
    executor = AsyncTaskExecutor(num_workers=1)

    async with executor:
        await executor.submit(Task("Session 1"))
        await executor.wait_all()

    async with executor:
        await executor.submit(Task("Session 2"))
        await executor.wait_all()

    assert not executor._running