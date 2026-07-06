from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")

# Persist a single Owner in the session "vault" so it survives Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)
owner = st.session_state.owner

# Let the user edit the owner's name and daily time budget on the live object.
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Available minutes per day", min_value=0, max_value=1440, value=owner.available_minutes
)

st.divider()

st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # Owner.add_pet() handles storing the new Pet on the persistent Owner.
    owner.add_pet(Pet(name=pet_name, species=species))
    st.success(f"Added {pet_name} ({species}).")

# The UI reflects the change simply by reading back from the persistent Owner.
pets = owner.list_pets()
if pets:
    st.write("Current pets:")
    for pet in pets:
        st.write(f"- {pet.name} ({pet.species}) — {len(pet.list_tasks())} task(s)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
st.caption("Tasks are added to a specific pet and feed into the scheduler.")

if not pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        # Scheduled time of day; stored on the Task as an "HH:MM" string.
        start = st.time_input("Start time", value=time(8, 0))

    # Choose which pet receives the task.
    pet_names = [pet.name for pet in pets]
    target_name = st.selectbox("For which pet?", pet_names)

    if st.button("Add task"):
        target_pet = pets[pet_names.index(target_name)]
        # Pet.add_task() stores the new Task on the chosen pet.
        target_pet.add_task(
            Task(
                name=task_title,
                duration=int(duration),
                priority=priority,
                start_time=start.strftime("%H:%M"),
            )
        )
        st.success(f"Added '{task_title}' to {target_name} at {start.strftime('%H:%M')}.")

    # Show each pet's tasks in chronological order using sort_by_time().
    for pet in pets:
        if pet.list_tasks():
            st.write(f"**{pet.name}'s tasks (by time):**")
            for task in Scheduler(pet.list_tasks(), owner.available_minutes).sort_by_time():
                st.write(f"- {task.summary()}")

st.divider()

st.subheader("Build Schedule")
st.caption("Runs your Scheduler on all of the owner's tasks within the time budget.")

if st.button("Generate schedule"):
    # Owner.build_scheduler() gathers every pet's tasks and hands them to a Scheduler.
    scheduler = owner.build_scheduler()
    scheduler.generate_plan()
    st.text(scheduler.explain())
