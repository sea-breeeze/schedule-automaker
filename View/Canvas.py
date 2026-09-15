import streamlit as st

st.title("Welcome to Schedule Automator")
st.write("Begin your journey here.")

worker_name = st.text_input("Enter your name: ")

availability = st.multiselect("Enter your availability: ", 
    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])


if st.button("Submit"):
    if not worker_name:
        st.error("Please enter your name.")
    elif not availability:
        st.error("Please select your availability.")
    else:
        st.success(f"Thank you, {worker_name}. Your availability has been recorded: {', '.join(availability)}.")

    