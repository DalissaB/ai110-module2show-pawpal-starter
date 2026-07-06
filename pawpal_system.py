"""PawPal+ logic layer.

Backend classes for the PawPal+ app. This is the "logic layer" where all
scheduling and data classes live, kept separate from the Streamlit UI.

Skeleton only — attributes and method stubs based on the UML. Logic is added
in later phases.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care task (e.g., a walk, feeding, or meds)."""

    name: str
    duration: int  # minutes
    priority: str  # e.g., "high", "medium", "low"

    def summary(self) -> str:
        """Return a short, human-readable description of the task."""
        raise NotImplementedError


@dataclass
class Pet:
    """An animal and the care tasks it needs."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The person using the app and their overall constraints."""

    name: str
    available_minutes: int
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet for this owner."""
        raise NotImplementedError

    def list_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        raise NotImplementedError


class Scheduler:
    """Turns tasks and constraints into a daily plan."""

    def __init__(self, tasks: list[Task], available_minutes: int) -> None:
        self.tasks = tasks
        self.available_minutes = available_minutes

    def sort_tasks(self) -> list[Task]:
        """Order tasks (e.g., by priority, then duration)."""
        raise NotImplementedError

    def generate_plan(self) -> list[Task]:
        """Pick and arrange tasks that fit within the time budget."""
        raise NotImplementedError

    def explain(self) -> str:
        """Describe why tasks were included or skipped."""
        raise NotImplementedError
