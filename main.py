"""PawPal+ demo script.

Builds a small owner/pet/task setup using the logic layer in
pawpal_system.py and prints today's schedule to the terminal.
"""

from pawpal_system import Owner, Pet, Scheduler, Task

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

    # At least three tasks with different durations.
    rex.add_task(Task("Morning walk", duration=30, priority="high"))
    rex.add_task(Task("Feed breakfast", duration=10, priority="high"))
    mia.add_task(Task("Feed breakfast", duration=5, priority="medium"))
    mia.add_task(Task("Vet meds", duration=15, priority="high"))
    rex.add_task(Task("Long groom", duration=45, priority="low"))

    # Show the pets that were created, along with each pet's tasks.
    print(f"{owner.name}'s pets:")
    for pet in owner.list_pets():
        print(f"  - {pet.name} ({pet.species})")
        for task in pet.list_tasks():
            print(f"      * {task.summary()}")
    print()

    # Build a schedule for each pet, giving every pet its own time budget.
    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for pet in owner.list_pets():
        scheduler = Scheduler(pet.list_tasks(), MINUTES_PER_PET)
        scheduler.generate_plan()
        print(f"\n{pet.name} ({pet.species}):")
        print(scheduler.explain())


if __name__ == "__main__":
    main()
