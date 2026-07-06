"""Simple tests for the PawPal+ logic layer."""

import os
import sys

# Make pawpal_system.py (in the repo root) importable from this subfolder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip the task from not-done to done."""
    task = Task("Morning walk", duration=30, priority="high")
    assert task.completed is False  # starts incomplete

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet(name="Rex", species="dog")
    assert len(pet.list_tasks()) == 0  # starts with no tasks

    pet.add_task(Task("Feed breakfast", duration=10, priority="high"))

    assert len(pet.list_tasks()) == 1
