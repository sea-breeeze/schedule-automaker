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
        st.success(f"Thank you, {worker_name}. Your availability has been recorded: {', '.join(availability)}.")
        worker = {
            "name": worker_name,
            "availability": availability
        }
        # Add the worker to the session state if the submit button is clicked and the input fields are filled
        st.session_state.workers.append(worker)

st.write("Current Workers and their Availability:")
# Display the list of workers and their availability
st.session_state.workers