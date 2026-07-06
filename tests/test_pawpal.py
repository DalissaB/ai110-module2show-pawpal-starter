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


# --- Sorting correctness: edge cases ---


def test_sort_by_time_leaves_original_list_unchanged():
    """sort_by_time() returns a new ordering without mutating self.tasks."""
    late = Task("Evening walk", duration=20, start_time="18:00")
    early = Task("Morning walk", duration=30, start_time="08:00")
    original_order = [late, early]

    scheduler = Scheduler(original_order, available_minutes=120)
    scheduler.sort_by_time()

    # The stored list is untouched; only the returned copy is sorted.
    assert scheduler.tasks == [late, early]


def test_sort_by_time_handles_non_zero_padded_times():
    """'8:00' must sort the same as '08:00' (minutes-since-midnight key)."""
    padded = Task("Padded", duration=10, start_time="08:00")
    unpadded_earlier = Task("Unpadded", duration=10, start_time="7:30")

    scheduler = Scheduler([padded, unpadded_earlier], available_minutes=120)

    assert scheduler.sort_by_time() == [unpadded_earlier, padded]


def test_sort_by_time_with_all_unscheduled_keeps_them_all():
    """When no task has a start_time, every task is still returned."""
    a = Task("A", duration=10)
    b = Task("B", duration=20)

    scheduler = Scheduler([a, b], available_minutes=120)

    result = scheduler.sort_by_time()
    assert len(result) == 2
    assert a in result and b in result


def test_sort_tasks_orders_by_priority_then_duration():
    """sort_tasks() ranks high < medium < low, breaking ties by shorter duration."""
    low = Task("Groom", duration=5, priority="low")
    high_long = Task("Walk", duration=30, priority="high")
    high_short = Task("Feed", duration=10, priority="high")

    scheduler = Scheduler([low, high_long, high_short], available_minutes=120)

    # Both high tasks come first; the shorter high task wins the tie.
    assert scheduler.sort_tasks() == [high_short, high_long, low]


def test_unknown_priority_sorts_last():
    """A priority the app doesn't recognize is ranked after known ones."""
    known = Task("Walk", duration=30, priority="low")
    unknown = Task("Mystery", duration=10, priority="urgent")

    scheduler = Scheduler([unknown, known], available_minutes=120)

    assert scheduler.sort_tasks() == [known, unknown]


# --- Recurrence logic: edge cases ---


def test_recurring_next_occurrence_preserves_task_details():
    """The next occurrence copies name, duration, priority, and start_time."""
    pet = Pet(name="Rex", species="dog")
    walk = Task(
        "Walk",
        duration=30,
        priority="high",
        frequency="daily",
        start_time="08:00",
        due_date=date(2026, 7, 5),
    )
    pet.add_task(walk)

    upcoming = pet.complete_task(walk)

    assert upcoming.name == "Walk"
    assert upcoming.duration == 30
    assert upcoming.priority == "high"
    assert upcoming.start_time == "08:00"
    assert upcoming.frequency == "daily"


def test_completing_task_twice_advances_the_date_each_time():
    """Each completion rolls the recurring task forward another day."""
    pet = Pet(name="Rex", species="dog")
    walk = Task("Walk", duration=30, frequency="daily", due_date=date(2026, 7, 5))
    pet.add_task(walk)

    first = pet.complete_task(walk)
    second = pet.complete_task(first)

    assert first.due_date == date(2026, 7, 6)
    assert second.due_date == date(2026, 7, 7)
    assert len(pet.list_tasks()) == 3  # original + two successors


# --- Conflict detection: edge cases ---


def test_three_tasks_at_same_time_produce_three_pairwise_conflicts():
    """Three clashing tasks yield all 3 pairwise conflicts (A-B, A-C, B-C)."""
    a = Task("Walk", duration=30, start_time="08:00")
    b = Task("Play", duration=10, start_time="08:00")
    c = Task("Feed", duration=5, start_time="08:00")

    scheduler = Scheduler([a, b, c], available_minutes=120)

    assert len(scheduler.find_conflicts()) == 3
    assert len(scheduler.conflict_warnings()) == 3


def test_conflict_check_ignores_unscheduled_tasks():
    """Two tasks with empty start_time never conflict with each other."""
    scheduler = Scheduler(
        [Task("Groom", duration=45), Task("Bathe", duration=20)],
        available_minutes=120,
    )

    assert scheduler.find_conflicts() == []


def test_conflict_check_is_string_based_not_time_based():
    """Known limitation: '8:00' and '08:00' are the same moment but are NOT
    flagged as a conflict, because find_conflicts() compares the raw strings.

    This test documents current behavior. If find_conflicts() is ever changed
    to normalize times (like sort_by_time does), update this assertion.
    """
    padded = Task("Walk", duration=30, start_time="08:00")
    unpadded = Task("Play", duration=10, start_time="8:00")

    scheduler = Scheduler([padded, unpadded], available_minutes=120)

    assert scheduler.find_conflicts() == []  # not detected as a clash today


# --- generate_plan / explain: the greedy budget logic ---


def test_generate_plan_on_empty_scheduler():
    """A scheduler with no tasks produces an empty plan without crashing."""
    scheduler = Scheduler([], available_minutes=60)

    assert scheduler.generate_plan() == []
    # Quirk: explain() can't tell "empty plan" from "never ran", so it returns
    # the not-generated message even after generate_plan() runs on no tasks.
    assert scheduler.explain() == "No plan generated yet. Call generate_plan() first."


def test_generate_plan_includes_task_that_fits_exactly():
    """A task whose duration equals the remaining budget is still included."""
    task = Task("Walk", duration=60, priority="high")
    scheduler = Scheduler([task], available_minutes=60)

    plan = scheduler.generate_plan()

    assert plan == [task]
    assert task.status == TaskStatus.TODO  # placed, not skipped


def test_generate_plan_skips_task_larger_than_budget():
    """A task too big for the whole budget is marked SKIPPED with a reason."""
    task = Task("Long groom", duration=90, priority="high")
    scheduler = Scheduler([task], available_minutes=60)

    plan = scheduler.generate_plan()

    assert plan == []
    assert task.status == TaskStatus.SKIPPED
    assert scheduler.skipped[0][0] is task


def test_generate_plan_prefers_high_priority_when_budget_is_tight():
    """High-priority tasks are placed first; low-priority loses out on time."""
    high = Task("Walk", duration=30, priority="high")
    low = Task("Groom", duration=20, priority="low")
    scheduler = Scheduler([high, low], available_minutes=40)

    plan = scheduler.generate_plan()

    # Only 40 min: high (30) fits, leaving 10 — not enough for low (20).
    assert plan == [high]
    assert low.status == TaskStatus.SKIPPED


def test_generate_plan_is_repeatable_across_runs():
    """Re-running generate_plan() resets stale SKIPPED marks and is stable."""
    high = Task("Walk", duration=30, priority="high")
    low = Task("Groom", duration=20, priority="low")
    scheduler = Scheduler([high, low], available_minutes=40)

    first = scheduler.generate_plan()
    second = scheduler.generate_plan()

    assert first == second == [high]
    assert low.status == TaskStatus.SKIPPED


def test_generate_plan_skips_already_completed_tasks():
    """A task already marked done is recorded as skipped, not re-added."""
    done = Task("Feed", duration=10, priority="high")
    done.mark_complete()
    todo = Task("Walk", duration=30, priority="high")
    scheduler = Scheduler([done, todo], available_minutes=60)

    plan = scheduler.generate_plan()

    assert plan == [todo]
    assert (done, "already completed") in scheduler.skipped
