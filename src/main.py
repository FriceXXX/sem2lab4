from datetime import datetime
import asyncio

from src.executor import AsyncTaskExecutor
from src.handler import PrintHandler
from src.task import Task
from src.exceptions import (
    InvalidTaskIdError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusError,
    TaskAlreadyCompletedError,
    InvalidStateTransitionError
)
from src.task_filters import ANDFilter, StatusFilter, PriorityFilter, ORFilter
from src.task_queue import TaskQueue


async def demonstrate_basic_execution():
    """Демонстрация базовой работы исполнителя"""
    print("Базовое выполнение задач" + "-"*60)


    executor = AsyncTaskExecutor(
        num_workers=2,
        handler=PrintHandler()
    )

    async with executor:
        tasks = [
            Task("Первая задача", priority=3),
            Task("Вторая задача", priority=5),
            Task("Третья задача", priority=1),
        ]

        for task in tasks:
            await executor.submit(task)

        print(f"\nКол-во задач в очереди: {executor.len_queue}\n")
        await executor.wait_all()
        print(f"\nКол-во задач в очереди: {executor.len_queue}")
        print(f"\nСтатус исполнителя: {executor}")



async def demonstrate_lazy_filter(): # from lab 3
    print("\n\nDemonstrating lazy filter" + "-" *60)
    queue = TaskQueue()

    tasks_data = [
        ("Срочная задача", 5, "created"),
        ("Обычная задача", 3, "created"),
        ("Низкий приоритет", 1, "created"),
        ("В работе", 4, "in_progress"),
        ("Почти готова", 4, "in_progress"),
        ("Завершена", 2, "completed"),
        ("Отменена", 3, "cancelled"),
    ]

    for desc, prio, stats in tasks_data:
        task = Task(description=desc, priority=prio, status=stats)
        await queue.put(task)

    print("\nActive: \n")
    active_tasks = queue.status_filter('in_progress')
    for task in active_tasks:
        print(f" {task.id}: {task.description}")

    print("\nHigh priority: \n")
    high_priority = queue.priority_filter(min_priority=4)
    for task in high_priority:
        print(f" {task.id}: приоритет {task.priority}")##

async def demonstrate_filter_classes():
    print("\n\nDemonstrating filters 2" + "-" *60)
    queue = TaskQueue()

    tasks_data = [
        ("Срочная задача", 5, "created"),
        ("Обычная задача", 3, "created"),
        ("Низкий приоритет", 1, "created"),
        ("В работе", 4, "in_progress"),
        ("Почти готова", 4, "in_progress"),
        ("Завершена", 2, "completed"),
        ("Отменена", 3, "cancelled"),
    ]

    for desc, prio, stats in tasks_data:
        task = Task(description=desc, priority=prio, status=stats)
        await queue.put(task)

    print("\nAND фильтр (статус 'in_progress' И приоритет >= 4) ---")
    and_filter = ANDFilter(
        StatusFilter('in_progress'),
        PriorityFilter(min_priority=4)
    )


    for task in queue.filter(and_filter):
        print(task)

    print("\nOR фильтр (статус 'in_progress' ИЛИ приоритет >= 4) ---")
    or_filter = ORFilter(
        StatusFilter('in_progress'),
        PriorityFilter(min_priority=4)
    )

    for task in queue.filter(or_filter):
        print(task)

    print()
    for task in queue:
        print(task)

if __name__ == "__main__":
    print("Demonstrating" + "-" *60)


    async def main():
        await demonstrate_basic_execution()

    asyncio.run(main())