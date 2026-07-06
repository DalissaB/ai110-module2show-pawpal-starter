"""PawPal+ logic layer.

Backend classes for the PawPal+ app. This is the "logic layer" where all
scheduling and data classes live, kept separate from the Streamlit UI.

Core implementation of the four classes from the UML:
Task, Pet, Owner, and Scheduler.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


# How many days to add to reach the next occurrence, per frequency.
_RECUR_DAYS = {"daily": 1, "weekly": 7}


# Lower number = more important. Used to order tasks in the scheduler.
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


class TaskStatus(str, Enum):
    """Where a task stands in today's plan."""

    TODO = "todo"  # not done yet
    DONE = "done"  # completed
    SKIPPED = "skipped"  # left out of the plan (e.g., no time left)


@dataclass
class Task:
    """A single pet care activity (e.g., a walk, feeding, or meds)."""

    name: str
    duration: int  # minutes the task takes
    priority: str = "medium"  # "high", "medium", or "low"
    frequency: str = "daily"  # e.g., "daily", "weekly", "once"
    start_time: str = ""  # scheduled time of day, e.g. "08:00" ("" = unscheduled)
    due_date: date = field(default_factory=date.today)  # day the task is due
    status: TaskStatus = TaskStatus.TODO

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        self.status = TaskStatus.DONE

    def next_occurrence(self) -> "Task | None":
        """Build the next scheduled instance of a recurring task.

        Reads this task's ``frequency`` and advances its ``due_date`` with
        ``timedelta`` ("daily" -> +1 day, "weekly" -> +7 days). The new Task is
        an otherwise-identical copy reset to TODO status.

        Returns:
            A fresh Task due on the next date, or None if the task does not
            repeat (e.g., frequency "once").
        """
        days = _RECUR_DAYS.get(self.frequency.lower())
        if days is None:
            return None  # non-recurring (e.g., "once")
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            start_time=self.start_time,
            due_date=self.due_date + timedelta(days=days),
            status=TaskStatus.TODO,
        )

    def mark_incomplete(self) -> None:
        """Reset this task back to not-done (todo)."""
        self.status = TaskStatus.TODO

    def mark_skipped(self) -> None:
        """Mark this task as skipped from today's plan."""
        self.status = TaskStatus.SKIPPED

    def priority_rank(self) -> int:
        """Numeric priority for sorting (unknown values sort last)."""
        return _PRIORITY_RANK.get(self.priority.lower(), len(_PRIORITY_RANK))

    def summary(self) -> str:
        """Return a short, human-readable description of the task."""
        when = f" at {self.start_time}" if self.start_time else ""
        return (
            f"{self.name}{when} — {self.duration} min, "
            f"{self.priority} priority, {self.frequency} "
            f"(due {self.due_date}) [{self.status.value}]"
        )


@dataclass
class Pet:
    """An animal and the care tasks it needs."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet (by identity)."""
        # Remove by identity so two look-alike tasks aren't confused.
        self.tasks = [t for t in self.tasks if t is not task]

    def list_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self.tasks)

    def complete_task(self, task: Task) -> "Task | None":
        """Mark a task done and roll a recurring task forward.

        Sets the task to DONE, then asks it for its next occurrence. If the task
        recurs, the new instance is appended to this pet's task list so the care
        routine continues automatically.

        Args:
            task: The task the owner just finished.

        Returns:
            The newly created next occurrence, or None if the task does not repeat.
        """
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            self.add_task(upcoming)
        return upcoming


@dataclass
class Owner:
    """The person using the app and their overall constraints."""

    name: str
    available_minutes: int
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet for this owner."""
        self.pets.append(pet)

    def list_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return list(self.pets)

    def all_tasks(self) -> list[Task]:
        """Gather every task across all of this owner's pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.list_tasks())
        return tasks

    def filter_tasks(self, pet_name=None, status=None) -> list[Task]:
        """Return tasks, optionally narrowed by pet and/or completion status.

        Args:
            pet_name: If given, keep only tasks belonging to the pet with this name.
            status: If given, keep only tasks with this TaskStatus. Because
                TaskStatus is a str Enum, a plain string like "done" also matches.

        Returns:
            The matching tasks (every task when no filters are supplied).
        """
        tasks: list[Task] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue  # skip pets we didn't ask for
            tasks.extend(pet.list_tasks())
        if status is not None:
            # TaskStatus is a str Enum, so this also matches plain strings
            # like "done" or "todo".
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def build_scheduler(self) -> "Scheduler":
        """Collect all pet tasks and hand them to a Scheduler with the time budget."""
        return Scheduler(self.all_tasks(), self.available_minutes)


class Scheduler:
    """Turns tasks and constraints into a daily plan.

    The "brain" of the app: it retrieves the owner's tasks, organizes them by
    priority, and manages which ones fit within the daily time budget.
    """

    def __init__(self, tasks: list[Task], available_minutes: int) -> None:
        """Store the tasks to schedule and the daily time budget."""
        self.tasks = tasks
        self.available_minutes = available_minutes
        # Filled in by generate_plan(); explain() reads these.
        self.plan: list[Task] = []
        self.skipped: list[tuple[Task, str]] = []

    def sort_tasks(self) -> list[Task]:
        """Order tasks by priority, then by shortest duration."""
        return sorted(self.tasks, key=lambda t: (t.priority_rank(), t.duration))

    def sort_by_time(self) -> list[Task]:
        """Return tasks in chronological order by their 'HH:MM' start_time.

        Each start_time is converted to minutes-since-midnight for the sort key,
        so ordering stays correct even if a value isn't zero-padded. Unscheduled
        tasks (empty start_time) sort to the end. The original list is unchanged.
        """
        # Convert "HH:MM" to minutes-since-midnight; "" (unscheduled) sorts last.
        def minutes(task: Task) -> float:
            if not task.start_time:
                return float("inf")
            hours, mins = task.start_time.split(":")
            return int(hours) * 60 + int(mins)

        return sorted(self.tasks, key=minutes)

    def find_conflicts(self) -> list[tuple[Task, Task]]:
        """Detect tasks scheduled at the same time of day.

        Compares every pair of *scheduled* tasks (those with a start_time) once
        and flags any two sharing the same start_time — whether they belong to
        the same pet or different pets. Unscheduled tasks are ignored.

        Returns:
            A list of conflicting (task_a, task_b) pairs (empty if none).
        """
        conflicts: list[tuple[Task, Task]] = []
        scheduled = [t for t in self.tasks if t.start_time]
        # Compare each pair once; two tasks clash if they start at the same time.
        for i, first in enumerate(scheduled):
            for second in scheduled[i + 1:]:
                if first.start_time == second.start_time:
                    conflicts.append((first, second))
        return conflicts

    def conflict_warnings(self) -> list[str]:
        """Return friendly warning strings for each same-time clash.

        A lightweight, non-crashing check: wraps find_conflicts() and formats
        each pair as a warning the UI or terminal can print. Returns an empty
        list when there are no conflicts.
        """
        return [
            f"⚠️ Conflict at {a.start_time}: '{a.name}' overlaps with '{b.name}'."
            for a, b in self.find_conflicts()
        ]

    def generate_plan(self) -> list[Task]:
        """Build today's plan with a greedy, priority-first strategy.

        Resets any stale SKIPPED marks (so re-running is repeatable), then walks
        tasks in priority order (via sort_tasks) and includes each one that still
        fits the remaining minutes. Completed tasks and tasks that don't fit are
        recorded as skipped, with a reason, for explain() to report.

        Returns:
            The list of tasks chosen for the plan.
        """
        plan: list[Task] = []
        skipped: list[tuple[Task, str]] = []
        remaining = self.available_minutes

        # Clear any prior "skipped" marks so re-running the plan is repeatable.
        for task in self.tasks:
            if task.status == TaskStatus.SKIPPED:
                task.mark_incomplete()

        for task in self.sort_tasks():
            if task.status == TaskStatus.DONE:
                skipped.append((task, "already completed"))
            elif task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration
            else:
                task.mark_skipped()
                skipped.append(
                    (task, f"needs {task.duration} min, only {remaining} left")
                )

        self.plan = plan
        self.skipped = skipped
        return plan

    def explain(self) -> str:
        """Describe why tasks were included or skipped."""
        if not self.plan and not self.skipped:
            return "No plan generated yet. Call generate_plan() first."

        used = sum(t.duration for t in self.plan)
        lines = [
            f"Daily plan: {len(self.plan)} task(s), "
            f"{used}/{self.available_minutes} min used.",
        ]
        for task in self.plan:
            lines.append(f"  ✓ {task.name} ({task.duration} min, {task.priority})")
        for task, reason in self.skipped:
            lines.append(f"  ✗ {task.name} — skipped: {reason}")
        return "\n".join(lines)
