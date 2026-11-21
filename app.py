"""PS59: Hospital Appointment Bot, a Streamlit classroom mini-project."""
from __future__ import annotations

from datetime import date, timedelta
import pandas as pd
import streamlit as st

from booking import BookingError, available_slots, book_slot, booked_appointments, ensure_demo_data
from llm_client import LLMError, extract_details

st.set_page_config(page_title="Hospital Appointment Bot | PS59", page_icon="🏥", layout="wide")
ensure_demo_data()

st.title("🏥 Hospital Appointment Bot")
st.caption("LLM Mini Project | Problem Statement 59 | Fictional hospital data - classroom demonstration only")
with st.sidebar:
    st.header("Model settings")
    provider = st.selectbox("LLM provider", ["Groq", "Ollama (local)"])
    st.info("Groq needs a GROQ_API_KEY in .env. Ollama needs a running local model. No model training required.")
    st.warning("Appointments here are saved to local CSV files, not to a real hospital.")

slots = available_slots()
if "extracted" not in st.session_state:
    st.session_state.extracted = None
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

left, right = st.columns([1.2, 1])
with left:
    st.subheader("1. Request an appointment")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    st.write("Example: *Book a Cardiology appointment for Rahul Patil on " + tomorrow + " at 10 AM.*")
    request = st.text_area("Type your request in natural language", height=115,
                           placeholder=f"My name is Rahul Patil. I need a cardiology appointment on {tomorrow} at 10 am.")
    if st.button("Analyze with LLM", type="primary", use_container_width=True):
        st.session_state.extracted = None
        st.session_state.last_input = request
        try:
            with st.spinner("Extracting details using the selected LLM..."):
                st.session_state.extracted = extract_details(request, provider)
        except LLMError as exc:
            st.error(str(exc))

    if st.session_state.extracted:
        st.subheader("2. Review extracted details")
        details = st.session_state.extracted
        st.json(details)
        missing = [field for field in ("patient_name", "department", "date", "time") if not details.get(field)]
        if missing:
            st.warning("Missing information: " + ", ".join(missing) + ". Add it to your request and analyze again.")
        else:
            st.write("Booking is **not automatic**. Click below only after checking the extracted values.")
            if st.button("Confirm and book available slot", use_container_width=True):
                try:
                    booking = book_slot(details["patient_name"], details["department"],
                                        details["date"], details["time"], details.get("doctor_name"))
                    st.success("Appointment confirmed in the local demo database!")
                    st.write("**Booking ID:**", booking["booking_id"])
                    st.write("**Doctor:**", booking["doctor"])
                    st.write("**Date and time:**", booking["date"], booking["time"])
                    st.session_state.extracted = None
                except BookingError as exc:
                    st.error(str(exc))

with right:
    st.subheader("Available doctor slots")
    if slots:
        df = pd.DataFrame(slots)[["doctor", "department", "date", "time"]]
        st.dataframe(df, hide_index=True, use_container_width=True, height=460)
        st.caption("Times are in 24-hour format; dates and doctors are fictitious.")
    else:
        st.info("No future demo slots are available. To reseed for a new demo, close the app and delete data/doctor_slots.csv and data/appointments.csv.")

with st.expander("Booking history (local demo CSV)"):
    records = booked_appointments()
    if records:
        st.dataframe(pd.DataFrame(records), hide_index=True, use_container_width=True)
    else:
        st.write("No appointments have been booked yet.")

st.caption("Privacy: use made-up patient names. This mini project is not connected to a hospital and does not provide medical advice.")
