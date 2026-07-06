"""PawPal+ logic layer.

Backend classes for the PawPal+ app. This is the "logic layer" where all
scheduling and data classes live, kept separate from the Streamlit UI.

Core implementation of the four classes from the UML:
Task, Pet, Owner, and Scheduler.
"""

from dataclasses import dataclass, field


# Lower number = more important. Used to order tasks in the scheduler.
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care activity (e.g., a walk, feeding, or meds)."""

    name: str
    duration: int  # minutes the task takes
    priority: str = "medium"  # "high", "medium", or "low"
    frequency: str = "daily"  # e.g., "daily", "twice daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task back to not-done."""
        self.completed = False

    def priority_rank(self) -> int:
        """Numeric priority for sorting (unknown values sort last)."""
        return _PRIORITY_RANK.get(self.priority.lower(), len(_PRIORITY_RANK))

    def summary(self) -> str:
        """Return a short, human-readable description of the task."""
        status = "done" if self.completed else "todo"
        return (
            f"{self.name} — {self.duration} min, "
            f"{self.priority} priority, {self.frequency} [{status}]"
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

    def generate_plan(self) -> list[Task]:
        """Greedily pick tasks in priority order that fit the time budget."""
        plan: list[Task] = []
        skipped: list[tuple[Task, str]] = []
        remaining = self.available_minutes

        for task in self.sort_tasks():
            if task.completed:
                skipped.append((task, "already completed"))
            elif task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration
            else:
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
