from datetime import datetime

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


def demonstrate_descriptors():

    print("\n\nDemonstrating descriptors"+"-" *60)

    try:
        task = Task("TASK-001", "Реализовать валидацию дескрипторов", priority=4)
        print(f"\nЗадача создана: {task.id}")

        print(f"  ID: {task.id}")
        print(f"  Описание: {task.description}")
        print(f"  Приоритет: {task.priority}")
        print(f"  Статус: {task.status}")

        print("\nПопытка установить некорректные значения:")

        try:
            task.id = "invalid id with spaces"
        except InvalidTaskIdError as e:
            print(f"Ошибка при установке ID: {e}")

        try:
            task.priority = 10
        except InvalidPriorityError as e:
            print(f"Ошибка при установке приоритета: {e}")

        try:
            task.description = ""
        except InvalidDescriptionError as e:
            print(f"Ошибка при установке описания: {e}")

    except Exception as e:
        print(f"Ошибка: {e}")


def demonstrate_properties():
    print("\n\nDemonstrating properties" + "-" *60)

    task = Task("TASK-002", "Изучить property в Python", priority=3)

    print(f"\nЗадача: {task.id}")
    print(f"  Время создания: {task.created_at.strftime('%H:%M:%S')}")
    print(f"  Активна: {task.is_active}")
    print(f"  Завершена: {task.is_completed}")
    print(f"  Возраст: {task.age:.2f} часов")

    try:
        task.created_at = datetime.now()
    except AttributeError as e:
        print(f"Нельзя изменить created_at: {e}")

    try:
        task.is_active = False
    except AttributeError as e:
        print(f"Нельзя установить is_active: {e}")


def demonstrate_state_transitions():
    print("\n\nDemonstrating state transitions" + "-" *60)
    task = Task("Реализовать коне(чный автомат задачи", priority=4)

    print(f"\nНачальное состояние: {task.status}")
    print(f"Активна: {task.is_active}")

    task.start()
    print(f"  После start(): статус = {task.status}, активна = {task.is_active}")

    task.complete()
    print(f"  После complete(): статус = {task.status}, активна = {task.is_active}")
    print(f"  Время завершения: {task.completed_at.strftime('%H:%M:%S')}")

    print("Завершаем завершенную")
    try:
        task.start()
    except TaskAlreadyCompletedError as e:
        print(f"{e}")

    try:
        task.update_priority(5)
    except TaskAlreadyCompletedError as e:
        print(f"{e}")


def demonstrate_invariants():
    print("\n\nDemonstrating invariants" + "-" *60)

    try:
        Task("Пустой ID", priority=3)
    except InvalidTaskIdError as e:
        print(f"{e}")

    try:
        Task("A" * 1001, priority=3)
    except InvalidDescriptionError as e:
        print(f"{e}")

    try:
        Task("Некорректный приоритет", priority=0)
    except InvalidPriorityError as e:
        print(f"{e}")

    try:
        Task("Некорректный статус", status="invalid")
    except InvalidStatusError as e:
        print(f"{e}")

    task = Task("Тест переходов", priority=3)

    task.start()
    task.cancel()

    try:
        task.complete()
    except InvalidStateTransitionError as e:
        print(f"{e}")


def demonstrate_non_data_descriptor():
    task1 = Task("Задача 1", priority=3)
    task2 = Task("Задача 2", priority=4)

    print(f"\n{task1.id}: is_active = {task1.is_active}")
    print(f"{task2.id}: is_active = {task2.is_active}")

    task1.start()
    task2.start()
    task2.complete()

    print(f"\nПосле изменений:")
    print(f"{task1.id}: is_active = {task1.is_active}")
    print(f"{task2.id}: is_active = {task2.is_active}")

    print(f"  task1.__dict__: {task1.__dict__.get('is_active', 'не найдено')}")
    print(f"  task2.__dict__: {task2.__dict__.get('is_active', 'не найдено')}")

def demonstrate_queue():
    print("\n\nDemonstrating queue" + "-" *60)
    queue = TaskQueue()
    print("\n Basic Iteration \n")

    for i in range(5):
        task = Task(f"{i}", priority=(i%5)+1)
        queue.add_task(task)

    print(queue)

    print("\nFOR iteration:")
    for task in queue:
        print(task)

    print("List: ", list(queue))


def multiple_iterations():
    print("\n\nMultiple iterations" + "-" *60)
    queue = TaskQueue()
    for i in range(5):
        task = Task(f"{i}", priority=(i%5)+1)
        queue.add_task(task)

    print(queue)

    print("\nПервый обход:")
    for task in queue:
        print(f"  {task.id}")

    print("\nВторой обход:")
    for task in queue:
        print(f"  {task.id}")

    iter1 = iter(queue)
    iter2 = iter(queue)
    print()
    print(f"  iter1: {next(iter1).id}")
    print(f"  iter2: {next(iter2).id}")
    print(f"  iter1: {next(iter1).id}")

def demonstrate_lazy_filter():
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
        queue.add_task(task)

    print("\nActive: \n")
    active_tasks = queue.status_filter('in_progress')
    for task in active_tasks:
        print(f" {task.id}: {task.description}")

    print("\nHigh priority: \n")
    high_priority = queue.priority_filter(min_priority=4)
    for task in high_priority:
        print(f" {task.id}: приоритет {task.priority}")

def demonstrate_filter_classes():
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
        queue.add_task(task)

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

    # demonstrate_descriptors()
    # # demonstrate_properties()
    # demonstrate_state_transitions()
    # demonstrate_invariants()
    # demonstrate_non_data_descriptor()
    # demonstrate_queue()
    # multiple_iterations()
    demonstrate_lazy_filter()
    demonstrate_filter_classes()