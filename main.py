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
    rex.add_task(Task("Long groom", duration=45, priority="low", start_time="15:00"))
    rex.add_task(Task("Morning walk", duration=30, priority="high", start_time="08:00"))
    mia.add_task(Task("Vet meds", duration=15, priority="high", start_time="12:30"))
    rex.add_task(Task("Feed breakfast", duration=10, priority="high", start_time="07:30"))
    mia.add_task(Task("Feed breakfast", duration=5, priority="medium", start_time="07:45"))

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


if __name__ == "__main__":
    main()
