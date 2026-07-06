from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus

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

    # Choose which pet receives the task and how often it repeats.
    pet_names = [pet.name for pet in pets]
    col_pet, col_freq = st.columns(2)
    with col_pet:
        target_name = st.selectbox("For which pet?", pet_names)
    with col_freq:
        frequency = st.selectbox("Repeats", ["daily", "weekly", "once"])

    if st.button("Add task"):
        target_pet = pets[pet_names.index(target_name)]
        # Pet.add_task() stores the new Task on the chosen pet.
        target_pet.add_task(
            Task(
                name=task_title,
                duration=int(duration),
                priority=priority,
                start_time=start.strftime("%H:%M"),
                frequency=frequency,
            )
        )
        st.success(f"Added '{task_title}' to {target_name} at {start.strftime('%H:%M')}.")

    # Show each pet's tasks in chronological order using sort_by_time().
    for pet in pets:
        pet_tasks = pet.list_tasks()
        if pet_tasks:
            st.write(f"**{pet.name}'s tasks (by time):**")
            ordered = Scheduler(pet_tasks, owner.available_minutes).sort_by_time()
            st.table(
                [
                    {
                        "Time": task.start_time or "—",
                        "Task": task.name,
                        "Duration": f"{task.duration} min",
                        "Priority": task.priority,
                        "Repeats": task.frequency,
                        "Status": task.status.value,
                    }
                    for task in ordered
                ]
            )

st.divider()

st.subheader("Complete a Task")
st.caption("Completing a daily/weekly task automatically schedules its next occurrence.")

# Pair each still-to-do task with its pet so we know where to add the next one.
todo_pairs = [
    (pet, task)
    for pet in pets
    for task in pet.list_tasks()
    if task.status == TaskStatus.TODO
]
if not todo_pairs:
    st.info("No tasks to complete yet.")
else:
    labels = [f"{pet.name}: {task.name} ({task.frequency})" for pet, task in todo_pairs]
    choice = st.selectbox("Which task did you finish?", labels)
    if st.button("Mark complete"):
        chosen_pet, chosen_task = todo_pairs[labels.index(choice)]
        # Pet.complete_task() marks it done and auto-creates the next occurrence.
        upcoming = chosen_pet.complete_task(chosen_task)
        if upcoming is not None:
            st.success(
                f"Done! Next '{upcoming.name}' scheduled for {upcoming.due_date}."
            )
        else:
            st.success(f"Done! '{chosen_task.name}' does not repeat.")

st.divider()

st.subheader("Browse Tasks")
st.caption("Filter the owner's tasks by pet and status, then view them sorted by priority.")

if not pets:
    st.info("Add a pet and some tasks to browse them here.")
else:
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_filter = st.selectbox("Pet", ["All pets"] + [pet.name for pet in pets])
    with fcol2:
        status_filter = st.selectbox("Status", ["All"] + [s.value for s in TaskStatus])

    # Owner.filter_tasks() narrows by pet and/or status (None means "no filter").
    filtered = owner.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        status=None if status_filter == "All" else status_filter,
    )
    # Present the filtered tasks in priority order via Scheduler.sort_tasks().
    ordered = Scheduler(filtered, owner.available_minutes).sort_tasks()
    if ordered:
        st.table(
            [
                {
                    "Priority": task.priority,
                    "Time": task.start_time or "—",
                    "Task": task.name,
                    "Duration": f"{task.duration} min",
                    "Status": task.status.value,
                }
                for task in ordered
            ]
        )
    else:
        st.info("No tasks match those filters.")

st.divider()

st.subheader("Build Schedule")
st.caption("Runs your Scheduler on all of the owner's tasks within the time budget.")

if pets:
    # Check for time clashes on every rerun so the owner is warned immediately.
    # find_conflicts() doesn't mutate any task, so it's safe to run here.
    live_scheduler = owner.build_scheduler()
    warnings = live_scheduler.conflict_warnings()
    if warnings:
        st.warning(
            f"**{len(warnings)} scheduling conflict(s) found.** "
            "These tasks are set for the same time — you can only be in one place "
            "at once, so consider moving one task in each pair to a different time."
        )
        for message in warnings:
            st.warning(message)
    else:
        st.success("No scheduling conflicts — every task has its own time. 🎉")

if st.button("Generate schedule"):
    # Owner.build_scheduler() gathers every pet's tasks and hands them to a Scheduler.
    scheduler = owner.build_scheduler()
    scheduler.generate_plan()

    used = sum(t.duration for t in scheduler.plan)
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Tasks planned", len(scheduler.plan))
    mcol2.metric("Minutes used", f"{used}/{scheduler.available_minutes}")
    mcol3.metric("Tasks skipped", len(scheduler.skipped))

    if scheduler.plan:
        st.success(f"Planned {len(scheduler.plan)} task(s) within the time budget.")
        # Show the chosen tasks in chronological order — how an owner reads a day.
        ordered_plan = Scheduler(scheduler.plan, scheduler.available_minutes).sort_by_time()
        st.table(
            [
                {
                    "Time": task.start_time or "—",
                    "Task": task.name,
                    "Duration": f"{task.duration} min",
                    "Priority": task.priority,
                }
                for task in ordered_plan
            ]
        )
    else:
        st.info("Nothing fit in the plan yet — add tasks or raise the time budget.")

    if scheduler.skipped:
        st.warning("Left out of today's plan:")
        st.table(
            [
                {"Task": task.name, "Duration": f"{task.duration} min", "Reason": reason}
                for task, reason in scheduler.skipped
            ]
        )
