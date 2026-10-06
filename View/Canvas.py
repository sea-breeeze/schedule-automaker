import streamlit as st
import csv
import io

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "workers" not in st.session_state:
    st.session_state.workers = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []


# --------------------------------------------------
# SCHEDULING FUNCTIONS
# --------------------------------------------------

def get_task_duration(task):
    return task["duration"]


def get_available_workers_for_day(workers, day):
    available_workers = []

    for worker in workers:
        if day in worker["availability"]:
            available_workers.append(worker)

    return available_workers


def initialize_worker_minutes(available_workers):
    worker_minutes = {}

    for worker in available_workers:
        worker_minutes[worker["name"]] = 0

    return worker_minutes


def assign_tasks(
    sorted_tasks,
    available_workers,
    worker_minutes,
    last_task_worker
):
    assignments = []

    for task in sorted_tasks:

        # Start with every available worker
        eligible_workers = available_workers

        # If the task rotates, try to avoid the worker
        # who performed it the previous day
        if task.get("rotating", False):
            last_worker = last_task_worker.get(task["name"])

            eligible_workers = [
                worker
                for worker in available_workers
                if worker["name"] != last_worker
            ]

        # If the previous worker is the only available worker,
        # allow them to receive the task again
        if not eligible_workers:
            eligible_workers = available_workers

        # Choose the worker with the lowest workload
        lowest_worker = min(
            eligible_workers,
            key=lambda worker: worker_minutes[worker["name"]]
        )

        assignment = {
            "worker": lowest_worker["name"],
            "task": task["name"],
            "duration": task["duration"]
        }

        assignments.append(assignment)

        # Add the task duration to this worker's workload
        worker_minutes[lowest_worker["name"]] += task["duration"]

        # Remember who received this rotating task
        if task.get("rotating", False):
            last_task_worker[task["name"]] = lowest_worker["name"]

    return assignments


def generate_weekly_schedule(workers, sorted_tasks, days):
    weekly_schedule = {}

    # Tracks rotating tasks while generating this week
    last_task_worker = {}

    for day in days:

        available_workers = get_available_workers_for_day(
            workers,
            day
        )

        if not available_workers:
            weekly_schedule[day] = []

        else:
            worker_minutes = initialize_worker_minutes(
                available_workers
            )

            assignments = assign_tasks(
                sorted_tasks,
                available_workers,
                worker_minutes,
                last_task_worker
            )

            weekly_schedule[day] = assignments

    return weekly_schedule


def display_schedule(weekly_schedule):

    for day, assignments in weekly_schedule.items():

        st.subheader(day)

        if not assignments:
            st.write("No tasks assigned.")

        else:
            for assignment in assignments:
                st.write(
                    f"**{assignment['worker']}** — "
                    f"{assignment['task']} "
                    f"({assignment['duration']} minutes)"
                )


def schedule_to_csv(weekly_schedule):
    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Day",
        "Worker",
        "Task",
        "Duration"
    ])

    for day, assignments in weekly_schedule.items():
        for assignment in assignments:
            writer.writerow([
                day,
                assignment["worker"],
                assignment["task"],
                assignment["duration"]
            ])

    return output.getvalue()

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("Schedule Automator")

st.write(
    "Add workers and tasks, then automatically create "
    "a balanced weekly schedule."
)


# --------------------------------------------------
# TABS
# --------------------------------------------------

worker_tab, task_tab, schedule_tab = st.tabs(
    ["Workers", "Tasks", "Schedule"]
)


# ==================================================
# WORKERS TAB
# ==================================================

with worker_tab:

    st.header("Workers")

    # -----------------------------
    # ADD WORKER
    # -----------------------------

    st.subheader("Add Worker")

    worker_name = st.text_input(
        "Worker name:",
        key="worker_name_input"
    )

    availability = st.multiselect(
        "Availability:",
        DAYS,
        key="worker_availability_input"
    )

    if st.button("Add Worker", key="add_worker_button"):

        if not worker_name:
            st.error("Please enter a worker name.")

        elif not availability:
            st.error("Please select at least one available day.")

        else:
            duplicate_found = False

            for worker in st.session_state.workers:
                if worker["name"] == worker_name:
                    duplicate_found = True
                    break

            if duplicate_found:
                st.error(
                    f"A worker named '{worker_name}' already exists."
                )

            else:
                worker = {
                    "name": worker_name,
                    "availability": availability
                }

                st.session_state.workers.append(worker)

                st.success(
                    f"Worker '{worker_name}' has been added."
                )


    # -----------------------------
    # CURRENT WORKERS
    # -----------------------------

    st.divider()

    st.subheader("Current Workers")

    if st.session_state.workers:

        for worker in st.session_state.workers:
            st.write(
                f"**{worker['name']}** — "
                f"{', '.join(worker['availability'])}"
            )

    else:
        st.info("No workers have been added yet.")


    # -----------------------------
    # EDIT / DELETE WORKER
    # -----------------------------

    if st.session_state.workers:

        st.divider()

        with st.expander("Edit or Delete Worker"):

            worker_names = [
                worker["name"]
                for worker in st.session_state.workers
            ]

            selected_worker = st.selectbox(
                "Select a worker:",
                worker_names,
                key="selected_worker"
            )

            selected_worker_data = None

            for worker in st.session_state.workers:
                if worker["name"] == selected_worker:
                    selected_worker_data = worker
                    break

            updated_availability = st.multiselect(
                "Update availability:",
                DAYS,
                default=selected_worker_data["availability"],
                key="updated_worker_availability"
            )

            if st.button(
                "Update Worker",
                key="update_worker_button"
            ):

                if not updated_availability:
                    st.error(
                        "Please select at least one available day."
                    )

                else:
                    selected_worker_data["availability"] = (
                        updated_availability
                    )

                    st.success(
                        f"Worker '{selected_worker}' has been updated."
                    )

            if st.button(
                "Delete Worker",
                key="delete_worker_button"
            ):

                st.session_state.workers.remove(
                    selected_worker_data
                )

                st.rerun()


# ==================================================
# TASKS TAB
# ==================================================

with task_tab:

    st.header("Tasks")

    # -----------------------------
    # ADD TASK
    # -----------------------------

    st.subheader("Add Task")

    task_name = st.text_input(
        "Task name:",
        key="task_name_input"
    )

    task_duration = st.number_input(
        "Duration in minutes:",
        min_value=1,
        key="task_duration_input"
    )

    rotating = st.checkbox(
        "Rotating task",
        key="rotating_task_input"
    )

    if st.button("Add Task", key="add_task_button"):

        if not task_name:
            st.error("Please enter a task name.")

        else:
            duplicate_found = False

            for task in st.session_state.tasks:
                if task["name"] == task_name:
                    duplicate_found = True
                    break

            if duplicate_found:
                st.error(
                    f"A task named '{task_name}' already exists."
                )

            else:
                task = {
                    "name": task_name,
                    "duration": task_duration,
                    "rotating": rotating
                }

                st.session_state.tasks.append(task)

                st.success(
                    f"Task '{task_name}' has been added."
                )


    # -----------------------------
    # CURRENT TASKS
    # -----------------------------

    st.divider()

    st.subheader("Current Tasks")

    if st.session_state.tasks:

        for task in st.session_state.tasks:

            rotation_text = (
                "Rotating"
                if task.get("rotating", False)
                else "Not Rotating"
            )

            st.write(
                f"**{task['name']}** — "
                f"{task['duration']} minutes — "
                f"{rotation_text}"
            )

    else:
        st.info("No tasks have been added yet.")


    # -----------------------------
    # EDIT / DELETE TASK
    # -----------------------------

    if st.session_state.tasks:

        st.divider()

        with st.expander("Edit or Delete Task"):

            task_names = [
                task["name"]
                for task in st.session_state.tasks
            ]

            selected_task = st.selectbox(
                "Select a task:",
                task_names,
                key="selected_task"
            )

            selected_task_data = None

            for task in st.session_state.tasks:
                if task["name"] == selected_task:
                    selected_task_data = task
                    break

            updated_duration = st.number_input(
                "Update duration:",
                min_value=1,
                value=selected_task_data["duration"],
                key="updated_task_duration"
            )

            updated_rotating = st.checkbox(
                "Rotating task",
                value=selected_task_data.get(
                    "rotating",
                    False
                ),
                key="updated_task_rotating"
            )

            if st.button(
                "Update Task",
                key="update_task_button"
            ):

                selected_task_data["duration"] = (
                    updated_duration
                )

                selected_task_data["rotating"] = (
                    updated_rotating
                )

                st.success(
                    f"Task '{selected_task}' has been updated."
                )

            if st.button(
                "Delete Task",
                key="delete_task_button"
            ):

                st.session_state.tasks.remove(
                    selected_task_data
                )

                st.rerun()


# ==================================================
# SCHEDULE TAB
# ==================================================

with schedule_tab:

    st.header("Weekly Schedule")

    if not st.session_state.workers:

        st.warning(
            "Add at least one worker before generating a schedule."
        )

    elif not st.session_state.tasks:

        st.warning(
            "Add at least one task before generating a schedule."
        )

    else:

        # Sort tasks from longest to shortest
        sorted_tasks = sorted(
            st.session_state.tasks,
            key=get_task_duration,
            reverse=True
        )

        # Generate the weekly schedule
        weekly_schedule = generate_weekly_schedule(
            st.session_state.workers,
            sorted_tasks,
            DAYS
        )

        # Display it
        display_schedule(weekly_schedule)

        csv_data = schedule_to_csv(weekly_schedule)

        st.download_button(
            label="Download Schedule as CSV",
            data=csv_data,
            file_name="weekly_schedule.csv",
            mime="text/csv"
        )