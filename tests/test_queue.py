import pytest
from src.task import Task
from src.task_queue import TaskQueue
from src.task_filters import StatusFilter, PriorityFilter, ANDFilter, ORFilter

class TestQueueTest:
    """Queue Tests"""
    @pytest.fixture
    def queue(self):
        queue = TaskQueue()
        tasks = [
            Task("Task 1", priority=3, status="created"),
            Task("Task 2", priority=5, status="in_progress"),
            Task("Task 3", priority=1, status="completed"),
            Task("Task 4", priority=4, status="created"),
        ]
        for task in tasks:
            queue.add_task(task)
        return queue

    def test_add_task(self):
        queue = TaskQueue()
        task = Task("Test")
        queue.add_task(task)

        assert len(queue) == 1
        assert queue.get_task(task.id) == task

    def test_remove_task(self):
        queue = TaskQueue()
        task = Task("Test")
        queue.add_task(task)

        removed = queue.remove_task(task.id)
        assert removed == task
        assert len(queue) == 0
        assert queue.remove_task("NONEXISTENT") is None

    def test_get_task(self):
        queue = TaskQueue()
        task = Task("Test")
        queue.add_task(task)

        assert queue.get_task(task.id) == task
        assert queue.get_task("NONEXISTENT") is None

    def test_contains(self):
        queue = TaskQueue()
        task = Task("Test")
        queue.add_task(task)

        assert task in queue
        assert "NONEXISTENT" not in queue

    def test_len(self):
        queue = TaskQueue()
        assert len(queue) == 0

        queue.add_task(Task("Task 1"))
        assert len(queue) == 1

        queue.add_task(Task("Task 2"))
        assert len(queue) == 2

    def test_getitem(self):
        queue = TaskQueue()
        task1 = Task("Task 1")
        task2 = Task("Task 2")
        queue.add_task(task1)
        queue.add_task(task2)

        assert queue[0] == task1
        assert queue[1] == task2

        with pytest.raises(IndexError):
            _ = queue[2]

    def test_iteration(self):
        queue = TaskQueue()
        task1 = Task("Task 1")
        task2 = Task("Task 2")
        task3 = Task("Task 3")
        queue.add_task(task1)
        queue.add_task(task2)
        queue.add_task(task3)

        result1 = [t.description for t in queue]
        assert result1 == [task1.description, task2.description, task3.description]

        result2 = [t.description for t in queue]
        assert result2 == [task1.description, task2.description, task3.description]

    def test_filter_by_status(self):
        queue = TaskQueue()
        task1 = Task("Task 1", status="created")
        task2 = Task("Task 2", status="in_progress")
        task3 = Task("Task 3", status="completed")
        queue.add_task(task1)
        queue.add_task(task2)
        queue.add_task(task3)

        created = list(queue.status_filter("created"))
        assert len(created) == 1
        assert created[0].id == task1.id

        in_progress = list(queue.status_filter("in_progress"))
        assert len(in_progress) == 1
        assert in_progress[0].id == task2.id

    def test_filter_by_priority(self):
        queue = TaskQueue()
        queue.add_task(Task("Task 1", priority=1))
        queue.add_task(Task("Task 2", priority=3))
        queue.add_task(Task("Task 3", priority=5))

        high = list(queue.priority_filter(min_priority=4))
        assert len(high) == 1
        assert high[0].priority == 5

        medium = list(queue.priority_filter(2, 4))
        assert len(medium) == 1
        assert medium[0].priority == 3

    def test_filter_active(self):
        queue = TaskQueue()
        task1 = Task("Task 1", status="created")
        task2 = Task("Task 2", status="in_progress")
        task3 = Task("Task 3", status="completed")
        queue.add_task(task1)
        queue.add_task(task2)
        queue.add_task(task3)

        active = list(queue.active_filter())
        assert len(active) == 2
        assert active[0].description == "Task 1"
