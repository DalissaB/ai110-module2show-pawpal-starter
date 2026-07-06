"""Simple tests for the PawPal+ logic layer."""

import os
import sys

# Make pawpal_system.py (in the repo root) importable from this subfolder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

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


def test_completing_recurring_task_creates_next_occurrence():
    """Completing a daily task should add a fresh one due the next day."""
    pet = Pet(name="Rex", species="dog")
    walk = Task("Walk", duration=30, frequency="daily", due_date=date(2026, 7, 5))
    pet.add_task(walk)

    upcoming = pet.complete_task(walk)

    # Original is marked done; a new todo occurrence is added for tomorrow.
    assert walk.status == TaskStatus.DONE
    assert upcoming is not None
    assert upcoming.status == TaskStatus.TODO
    assert upcoming.due_date == date(2026, 7, 5) + timedelta(days=1)
    assert len(pet.list_tasks()) == 2


def test_weekly_task_advances_seven_days_and_once_does_not_recur():
    """Weekly recurs +7 days; a non-recurring task returns no next occurrence."""
    pet = Pet(name="Mia", species="cat")
    groom = Task("Groom", duration=45, frequency="weekly", due_date=date(2026, 7, 5))
    vet = Task("Vet visit", duration=60, frequency="once", due_date=date(2026, 7, 5))
    pet.add_task(groom)
    pet.add_task(vet)

    next_groom = pet.complete_task(groom)
    next_vet = pet.complete_task(vet)

    assert next_groom.due_date == date(2026, 7, 12)  # +7 days
    assert next_vet is None  # "once" does not repeat
    assert len(pet.list_tasks()) == 3  # groom's successor added, vet's not


def test_scheduler_detects_same_time_conflict():
    """Two tasks at the same start_time should produce a warning, not a crash."""
    walk = Task("Walk", duration=30, start_time="08:00")
    play = Task("Play", duration=10, start_time="08:00")  # clashes with walk
    feed = Task("Feed", duration=5, start_time="07:30")  # no clash
    unscheduled = Task("Groom", duration=45)  # no time, never conflicts

    scheduler = Scheduler([walk, play, feed, unscheduled], available_minutes=120)

    conflicts = scheduler.find_conflicts()
    warnings = scheduler.conflict_warnings()

    assert (walk, play) in conflicts
    assert len(conflicts) == 1
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_scheduler_reports_no_conflicts_when_times_differ():
    """Distinct start_times (and unscheduled tasks) yield no warnings."""
    scheduler = Scheduler(
        [
            Task("Walk", duration=30, start_time="08:00"),
            Task("Feed", duration=5, start_time="09:00"),
            Task("Groom", duration=45),  # unscheduled
        ],
        available_minutes=120,
    )

    assert scheduler.find_conflicts() == []
    assert scheduler.conflict_warnings() == []
