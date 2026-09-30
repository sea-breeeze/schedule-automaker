import streamlit as st

#Title and description of the app
st.title("Welcome to Schedule Automator")
st.write("Begin your journey here.")

# returns the input of the worker's name 
worker_name = st.text_input("Enter your name: ")

# returns the input of the worker's availability as a list of selected days
availability = st.multiselect("Enter your availability: ", 
    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

# Initialize the workers list in the session state if it doesn't exist
if "workers" not in st.session_state:
    st.session_state.workers = []

# conditionally checking if the submit button is clicked and if the input fields are filled
if st.button("Submit"):
    if not worker_name:
        st.error("Please enter your name.")
    elif not availability:
        st.error("Please select your availability.")
    else:
        duplicate_found = False

        for worker in st.session_state.workers:
            if worker["name"] == worker_name:
                duplicate_found = True
                break
        if duplicate_found:
            st.error(f"Duplicate entry found for {worker_name}. Please enter a unique name.")
        else:
            st.success(f"Thank you, {worker_name}. Your availability has been recorded: {', '.join(availability)}.")
            worker = {
                "name": worker_name,
                "availability": availability
            }
            # Add the worker to the session state if the submit button is clicked and the input fields are filled
            st.session_state.workers.append(worker)

duplicate_found = False

st.write("Current Workers and their Availability:")
# Display the list of workers and their availability
for worker in st.session_state.workers:
    st.write(f"Name: {worker['name']}, Availability: {', '.join(worker['availability'])}")

st.write("Tasks")

task_name = st.text_input("Enter a task: ")
task_duration = st.number_input("Enter the duration of the task in minutes: ", min_value=1)

st.write(task_name, task_duration)

if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.session_state.tasks.append(task);