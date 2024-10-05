import streamlit as st
import pandas as pd
import datetime

# Initialize session state for reports
if "reports" not in st.session_state:
    st.session_state["reports"] = []

# Function to add a new report
def add_report(location, hazard_type, description, date, time):
    report = {
        "Location": location,
        "Hazard Type": hazard_type,
        "Description": description,
        "Date": date,
        "Time": time
    }
    st.session_state["reports"].append(report)

# Streamlit app layout for community engagement
st.sidebar.title("Community Engagement")
st.sidebar.subheader("Report Environmental Hazards")

# Input fields for reporting hazards
report_location = st.sidebar.text_input("Location")
report_hazard_type = st.sidebar.selectbox("Hazard Type", ["Flood", "Pollution", "Other"])
report_description = st.sidebar.text_area("Description")
report_date = st.sidebar.date_input("Date", datetime.date.today())
report_time = st.sidebar.time_input("Time", datetime.datetime.now().time())

# Button to submit the report
if st.sidebar.button("Submit Report"):
    add_report(report_location, report_hazard_type, report_description, report_date, report_time)
    st.sidebar.success("Report submitted successfully!")

# Display the reports
st.subheader("Community Reports")
if st.session_state["reports"]:
    reports_df = pd.DataFrame(st.session_state["reports"])
    st.dataframe(reports_df)
else:
    st.write("No reports submitted yet.")
