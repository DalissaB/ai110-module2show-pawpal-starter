"""PawPal+ logic layer.

Backend classes for the PawPal+ app. This is the "logic layer" where all
scheduling and data classes live, kept separate from the Streamlit UI.

Core implementation of the four classes from the UML:
Task, Pet, Owner, and Scheduler.
"""

from dataclasses import dataclass, field
from enum import Enum


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
    frequency: str = "daily"  # e.g., "daily", "twice daily", "weekly"
    start_time: str = ""  # scheduled time of day, e.g. "08:00" ("" = unscheduled)
    status: TaskStatus = TaskStatus.TODO

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        self.status = TaskStatus.DONE

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
            f"{self.priority} priority, {self.frequency} [{self.status.value}]"
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
        """Return tasks, optionally limited to one pet and/or one status."""
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
        """Order tasks chronologically by 'HH:MM' start_time (unscheduled last)."""
        # Convert "HH:MM" to minutes-since-midnight; "" (unscheduled) sorts last.
        def minutes(task: Task) -> float:
            if not task.start_time:
                return float("inf")
            hours, mins = task.start_time.split(":")
            return int(hours) * 60 + int(mins)

        return sorted(self.tasks, key=minutes)

    def generate_plan(self) -> list[Task]:
        """Greedily pick tasks in priority order that fit the time budget."""
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
