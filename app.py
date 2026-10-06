from pathlib import Path
from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption("Daily pet care planning assistant")

with st.sidebar:
    st.header("Owner")
    owner_name = st.text_input("Owner name", value=owner.name)
    if st.button("Update owner"):
        owner.name = owner_name
        st.success("Owner updated.")

    st.header("Save / load")
    save_path = Path(__file__).with_name("pawpal_data.json")
    if st.button("Save JSON"):
        owner.save_to_json(save_path)
        st.success(f"Saved to {save_path.name}")
    if st.button("Load JSON"):
        try:
            st.session_state.owner = Owner.load_from_json(save_path)
            st.success(f"Loaded from {save_path.name}")
        except FileNotFoundError:
            st.warning("No saved file found yet. Create a pet and task first.")

st.subheader("Pets")
pet_name = st.text_input("Add pet name", value="Mochi")
species = st.selectbox("Pet species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.warning("Please enter a pet name.")
    elif owner.get_pet(pet_name) is not None:
        st.warning(f"{pet_name} is already on your roster.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
        st.success(f"Added {pet_name.strip()} the {species}.")

if owner.pets:
    pet_options = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Selected pet", pet_options)
else:
    selected_pet_name = None
    st.info("No pets yet. Add one to begin scheduling care tasks.")

st.divider()

st.subheader("Add a task")
if selected_pet_name:
    selected_pet = owner.get_pet(selected_pet_name)
    with st.form("task_form"):
        task_title = st.text_input("Task title", value="Morning walk")
        task_time = st.text_input("Time (HH:MM)", value="08:00")
        duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, step=5, value=30)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["none", "daily", "weekly"], index=0)
        task_description = st.text_area("Notes", value="")

        if st.form_submit_button("Add task"):
            try:
                task = Task(
                    title=task_title,
                    start_time=task_time,
                    duration=int(duration),
                    priority=priority,
                    frequency=frequency,
                    description=task_description,
                )
                selected_pet.add_task(task)
                st.success(f"Added {task_title} for {selected_pet_name}.")
            except ValueError as exc:
                st.error(str(exc))

    st.divider()

    all_tasks = owner.get_all_tasks(include_completed=True)
    if all_tasks:
        st.subheader("Current tasks")
        task_rows = []
        for task in sorted(all_tasks, key=lambda item: (item.pet_name or "", item.task_date, item.start_time)):
            task_rows.append(
                {
                    "Pet": task.pet_name,
                    "Task": task.title,
                    "Time": task.start_time,
                    "Date": task.task_date.isoformat(),
                    "Priority": task.priority,
                    "Duration": f"{task.duration} min",
                    "Frequency": task.frequency,
                    "Status": "Complete" if task.completed else "Open",
                }
            )
        st.table(task_rows)

        for pet in owner.pets:
            for task_index, task in enumerate(pet.tasks):
                if not task.completed and st.button(
                    f"Mark complete: {task.title} ({pet.name})",
                    key=f"complete_{pet.name}_{task_index}",
                ):
                    next_task = scheduler.mark_task_complete(task)
                    if next_task:
                        st.success(f"Completed task. Next occurrence is {next_task.task_date.isoformat()}.")
                    else:
                        st.success("Task marked complete.")
                    st.rerun()

    today_tasks = [
        task for task in owner.get_all_tasks(include_completed=False)
        if task.task_date == date.today()
    ]
    conflicts = scheduler.detect_conflicts(today_tasks)
    if conflicts:
        st.warning("Conflict warning: tasks share the same start time today.")
        for conflict in conflicts:
            st.write(f"{conflict['pet']} at {conflict['time']}: {', '.join(conflict['tasks'])}")

    st.divider()

    st.subheader("Find an open time")
    slot_duration = st.number_input("Task duration (minutes)", min_value=5, max_value=240, step=5, value=15)
    earliest_start = st.text_input("Earliest start time", value="07:00")
    if st.button("Find next available slot"):
        try:
            available_slot = scheduler.find_next_available_slot(
                duration=int(slot_duration),
                start_time=earliest_start,
            )
            if available_slot is None:
                st.warning("No available slot fits before the end of the day.")
            else:
                st.success(f"Next available {slot_duration}-minute slot: {available_slot}")
        except ValueError as exc:
            st.error(str(exc))

    if st.button("Generate schedule"):
        plan = scheduler.build_daily_plan(selected_pet_name)
        if not plan:
            st.info("No scheduled tasks yet.")
        else:
            st.subheader(f"Schedule for {selected_pet_name}")
            schedule_rows = [
                {
                    "Time": task.start_time,
                    "Task": task.title,
                    "Priority": task.priority,
                    "Duration": task.duration,
                    "Frequency": task.frequency,
                }
                for task in plan
            ]
            st.table(schedule_rows)
else:
    st.info("Add a pet first so PawPal+ can start planning tasks.")
