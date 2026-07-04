import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# Make sure the owner and scheduler exist in session state before anything else runs.
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# --- Owner section ---
st.subheader("Owner")

CATEGORY_OPTIONS = ["walk", "feeding", "meds", "enrichment", "grooming", "other"]
TIME_OF_DAY_OPTIONS = ["morning", "afternoon", "evening", "night"]

owner_name_col, owner_time_col = st.columns(2)
with owner_name_col:
    owner_name = st.text_input("Owner name")
with owner_time_col:
    owner_time_available = st.number_input(
        "Minutes available today", min_value=10, max_value=500, value=90
    )

preferred_categories = st.multiselect("Preferred categories", CATEGORY_OPTIONS)
preferred_times_of_day = st.multiselect("Preferred times of day", TIME_OF_DAY_OPTIONS)

if st.button("Save Owner"):
    try:
        owner = Owner(
            name=owner_name,
            time_available=int(owner_time_available),
            preferred_categories=preferred_categories,
            preferred_times_of_day=preferred_times_of_day,
        )
    except ValueError as e:
        st.error(str(e))
    else:
        st.session_state.owner = owner
        st.success("Owner added successfully.")

st.divider()
# --- Pet section ---
if st.session_state.owner is not None:
    st.subheader("Pet section")

    SPECIES_OPTIONS = ["dog", "cat", "bird", "rabbit", "other"]

    pet_name_col, pet_age_col = st.columns(2)
    with pet_name_col:
        pet_name = st.text_input("Pet name")
    with pet_age_col:
        pet_age = st.number_input("Pet age", min_value=1, max_value=30, value=1)

    species_choice = st.selectbox("Species", SPECIES_OPTIONS)
    if species_choice == "other":
        pet_species = st.text_input("Enter species")
    else:
        pet_species = species_choice

    if st.button("Add Pet"):
        try:
            pet = Pet(name=pet_name, species=pet_species, age=int(pet_age))
            st.session_state.owner.add_pet(pet)
        except ValueError as e:
            st.error(str(e))
        else:
            st.success(f"{pet.name} was added successfully.")

    pets = st.session_state.owner.get_list_of_pets()
    if pets:
        st.write("Current pets:")
        st.table(
            [{"Name": pet.name, "Species": pet.species, "Age": pet.age} for pet in pets]
        )

        pet_to_remove_name = st.selectbox("Select a pet to remove", [pet.name for pet in pets])
        if st.button("Remove Pet"):
            pet_to_remove = next(pet for pet in pets if pet.name == pet_to_remove_name)
            try:
                st.session_state.owner.remove_pet(pet_to_remove)
            except ValueError as e:
                st.error(str(e))
            else:
                st.success(f"{pet_to_remove.name} was removed successfully.")
    else:
        st.info("No pets added yet.")

st.divider()
# --- Task section ---
if st.session_state.owner is not None and st.session_state.owner.get_list_of_pets():
    st.subheader("Task section")

    PRIORITY_OPTIONS = ["low", "medium", "high"]
    FREQUENCY_OPTIONS = ["daily", "weekly", "as_needed"]
    TIME_OPTIONS = [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in (0, 30)]

    task_pets = st.session_state.owner.get_list_of_pets()
    task_pet_name = st.selectbox("Select a pet", [pet.name for pet in task_pets])
    task_pet = next(pet for pet in task_pets if pet.name == task_pet_name)

    task_col1, task_col2, task_col3 = st.columns(3)
    with task_col1:
        task_name = st.text_input("Task name")
        task_category_choice = st.selectbox("Category", CATEGORY_OPTIONS)
        if task_category_choice == "other":
            task_category = st.text_input("Enter category")
        else:
            task_category = task_category_choice

    with task_col2:
        task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=10)
        task_priority = st.selectbox("Priority", PRIORITY_OPTIONS, index=0)

    with task_col3:
        task_frequency = st.selectbox("Frequency", FREQUENCY_OPTIONS)
        any_time = st.checkbox("Any time")
        if not any_time:
            task_time = st.selectbox("Time", TIME_OPTIONS)
        else:
            task_time = ""

    if st.button("Add Task"):
        try:
            task = Task(
                category=task_category,
                duration=int(task_duration),
                priority=task_priority,
                name=task_name,
                frequency=task_frequency,
                time_of_day=task_time,
            )
            task_pet.add_task(task)
        except ValueError as e:
            st.error(str(e))
        else:
            st.success(f"{task.name} was added to {task_pet.name}.")

    st.write("Tasks by pet:")
    for pet in task_pets:
        st.markdown(f"**{pet.name}**")
        if pet.get_tasks():
            st.table(
                [
                    {
                        "Name": task.name,
                        "Category": task.category,
                        "Duration": task.duration,
                        "Priority": task.priority,
                        "Frequency": task.frequency,
                        "Time": task.time_of_day if task.time_of_day else "Anytime",
                    }
                    for task in pet.get_tasks()
                ]
            )
        else:
            st.caption("No tasks yet.")

st.divider()
# --- Generate schedule section ---
if st.session_state.owner is not None and st.session_state.owner.get_list_of_pets():
    st.subheader("Generate Schedule")

    if st.button("Generate Schedule"):
        owner = st.session_state.owner
        total_tasks = sum(pet.task_count() for pet in owner.get_list_of_pets())
        if total_tasks == 0:
            st.error("No tasks were added. Please add tasks.")
        else:
            scheduler = Scheduler(owner=owner)
            scheduler.generate_plan()
            st.session_state.scheduler = scheduler

    scheduler = st.session_state.scheduler
    if scheduler is not None:
        time_used = sum(task.duration for _, task in scheduler.scheduled_tasks)

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Time Committed", f"{time_used} / {scheduler.owner.time_available} min")
        with metric_col2:
            st.metric("Tasks Scheduled", len(scheduler.scheduled_tasks))
        with metric_col3:
            st.metric("Tasks Skipped", len(scheduler.skipped_tasks))

        st.write("Scheduled Tasks:")
        if scheduler.scheduled_tasks:
            st.table(
                [
                    {
                        "Pet": pet.name,
                        "Task": task.name,
                        "Time": task.time_of_day if task.time_of_day else "Anytime",
                        "Duration": task.duration,
                        "Priority": task.priority,
                    }
                    for pet, task in scheduler.scheduled_tasks
                ]
            )
        else:
            st.caption("No tasks scheduled.")

        st.write("Skipped Tasks:")
        if scheduler.skipped_tasks:
            st.table(
                [
                    {
                        "Pet": pet.name,
                        "Task": task.name,
                        "Time": task.time_of_day if task.time_of_day else "Anytime",
                        "Duration": task.duration,
                        "Priority": task.priority,
                    }
                    for pet, task in scheduler.skipped_tasks
                ]
            )
        else:
            st.caption("No tasks skipped.")

        st.write("Reasoning:")
        st.text(scheduler.explain_reasoning())
