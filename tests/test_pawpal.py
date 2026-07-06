"""Simple tests for the PawPal+ logic layer."""

import os
import sys

# Make pawpal_system.py (in the repo root) importable from this subfolder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip the task from todo to done."""
    task = Task("Morning walk", duration=30, priority="high")
    assert task.status == TaskStatus.TODO  # starts not-done

    task.mark_complete()

    assert task.status == TaskStatus.DONE


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet(name="Rex", species="dog")
    assert len(pet.list_tasks()) == 0  # starts with no tasks

    pet.add_task(Task("Feed breakfast", duration=10, priority="high"))

    assert len(pet.list_tasks()) == 1


def test_sort_by_time_orders_chronologically():
    """sort_by_time() should order tasks by start_time, unscheduled ones last."""
    late = Task("Evening walk", duration=20, start_time="18:00")
    early = Task("Morning walk", duration=30, start_time="08:00")
    unscheduled = Task("Groom", duration=15)  # no start_time

    scheduler = Scheduler([late, unscheduled, early], available_minutes=120)

    ordered = scheduler.sort_by_time()

    assert ordered == [early, late, unscheduled]


def test_filter_tasks_by_pet_and_status():
    """filter_tasks() should narrow tasks by pet name and/or status."""
    rex = Pet(name="Rex", species="dog")
    mia = Pet(name="Mia", species="cat")
    rex.add_task(Task("Walk", duration=30))
    rex_done = Task("Feed", duration=10)
    rex_done.mark_complete()
    rex.add_task(rex_done)
    mia.add_task(Task("Vet meds", duration=15))

    owner = Owner(name="Dalissa", available_minutes=60)
    owner.add_pet(rex)
    owner.add_pet(mia)

    # Filter by pet name.
    assert len(owner.filter_tasks(pet_name="Rex")) == 2
    assert len(owner.filter_tasks(pet_name="Mia")) == 1

    # Filter by status.
    assert len(owner.filter_tasks(status=TaskStatus.DONE)) == 1

    # Combine both filters.
    todo_for_rex = owner.filter_tasks(pet_name="Rex", status=TaskStatus.TODO)
    assert len(todo_for_rex) == 1
    assert todo_for_rex[0].name == "Walk"
