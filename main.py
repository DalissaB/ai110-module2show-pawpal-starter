"""PawPal+ demo script.

Builds a small owner/pet/task setup using the logic layer in
pawpal_system.py and prints today's schedule to the terminal.
"""

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus

# Daily time budget given to each pet.
MINUTES_PER_PET = 60


def main() -> None:
    # An owner with a daily time budget.
    owner = Owner(name="Dalissa", available_minutes=60, preferences="mornings")

    # At least two pets.
    rex = Pet(name="Rex", species="dog")
    mia = Pet(name="Mia", species="cat")
    owner.add_pet(rex)
    owner.add_pet(mia)

    # Tasks are added OUT OF CHRONOLOGICAL ORDER on purpose, so the
    # sort_by_time() demo below has something real to reorder.
    rex.add_task(
        Task("Long groom", duration=45, priority="low", start_time="15:00", frequency="weekly")
    )
    rex.add_task(Task("Morning walk", duration=30, priority="high", start_time="08:00"))
    mia.add_task(Task("Vet meds", duration=15, priority="high", start_time="12:30"))
    rex.add_task(Task("Feed breakfast", duration=10, priority="high", start_time="07:30"))
    mia.add_task(Task("Feed breakfast", duration=5, priority="medium", start_time="07:45"))
    # Deliberately clashes with Rex's "Morning walk" at 08:00 (same-time conflict).
    mia.add_task(Task("Play time", duration=10, priority="low", start_time="08:00"))

    # Mark one task done so the status filter has something to find.
    mia.list_tasks()[0].mark_complete()  # Mia's "Vet meds"

    # Show the pets that were created, along with each pet's tasks (add order).
    print(f"{owner.name}'s pets:")
    for pet in owner.list_pets():
        print(f"  - {pet.name} ({pet.species})")
        for task in pet.list_tasks():
            print(f"      * {task.summary()}")
    print()

    # --- Sorting: put every task in chronological order by start_time. ---
    print("=" * 40)
    print("All tasks sorted by time")
    print("=" * 40)
    scheduler = Scheduler(owner.all_tasks(), owner.available_minutes)
    for task in scheduler.sort_by_time():
        print(f"  {task.summary()}")
    print()

    # --- Conflict detection: warn (don't crash) on same-time tasks. ---
    print("=" * 40)
    print("Conflict detection")
    print("=" * 40)
    warnings = scheduler.conflict_warnings()
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("No scheduling conflicts found.")
    print()

    # --- Filtering: by pet name and by completion status. ---
    print("=" * 40)
    print("Filtering")
    print("=" * 40)
    print("Rex's tasks only:")
    for task in owner.filter_tasks(pet_name="Rex"):
        print(f"  {task.summary()}")

    print("\nStill to do (status == todo):")
    for task in owner.filter_tasks(status=TaskStatus.TODO):
        print(f"  {task.summary()}")

    print("\nAlready done (status == done):")
    for task in owner.filter_tasks(status=TaskStatus.DONE):
        print(f"  {task.summary()}")
    print()

    # Build a schedule for each pet, giving every pet its own time budget.
    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for pet in owner.list_pets():
        pet_scheduler = Scheduler(pet.list_tasks(), MINUTES_PER_PET)
        pet_scheduler.generate_plan()
        print(f"\n{pet.name} ({pet.species}):")
        print(pet_scheduler.explain())

    # --- Recurring tasks: completing one auto-creates the next occurrence. ---
    print("\n" + "=" * 40)
    print("Recurring tasks")
    print("=" * 40)
    walk = next(t for t in rex.list_tasks() if t.name == "Morning walk")  # daily
    groom = next(t for t in rex.list_tasks() if t.name == "Long groom")  # weekly

    for task in (walk, groom):
        print(f"\nCompleting: {task.summary()}")
        upcoming = rex.complete_task(task)
        print(f"  -> next occurrence: {upcoming.summary()}")


if __name__ == "__main__":
    main()
