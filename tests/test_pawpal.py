import os
import sys

# Make sure pawpal_system.py (at the project root) is importable regardless
# of the directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    """Task Completion: calling mark_complete() should flip is_completed to True."""
    task = Task(category="walk", duration=20, priority="high", name="Morning walk")
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet should increase that pet's task count."""
    pet = Pet(name="Mochi", species="cat", age=2)
    assert pet.task_count() == 0

    task = Task(category="feeding", duration=10, priority="medium", name="Feeding")
    pet.add_task(task)

    assert pet.task_count() == 1
