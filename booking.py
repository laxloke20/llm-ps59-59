"""Local demo CSV booking engine. It never interacts with a real hospital."""
from __future__ import annotations

import csv
import os
import tempfile
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

from filelock import FileLock

DEPARTMENTS = ("General Medicine", "Cardiology", "Dermatology", "Orthopedics", "Pediatrics")
SLOT_FIELDS = ("slot_id", "doctor", "department", "date", "time", "status", "patient_name")
BOOKING_FIELDS = ("booking_id", "slot_id", "patient_name", "doctor", "department", "date", "time", "booked_at")
DOCTORS = {
    "General Medicine": ("Dr. Asha Patil", ("09:00", "10:00", "11:00")),
    "Cardiology": ("Dr. Riya Deshmukh", ("10:00", "11:00", "14:00")),
    "Dermatology": ("Dr. Neel Shah", ("09:30", "12:00", "15:00")),
    "Orthopedics": ("Dr. Aman Kulkarni", ("10:30", "13:00", "16:00")),
    "Pediatrics": ("Dr. Tara Joshi", ("09:00", "11:30", "15:30")),
}

class BookingError(ValueError):
    """Invalid booking or requested slot unavailable."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _atomic_write(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".temp_", suffix=".csv", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def ensure_demo_data(data_dir: str | Path = "data") -> None:
    """Seed fictional doctors and slots, once; existing bookings are preserved."""
    folder = Path(data_dir)
    folder.mkdir(parents=True, exist_ok=True)
    slots_file, bookings_file = folder / "doctor_slots.csv", folder / "appointments.csv"
    with FileLock(str(folder / ".booking.lock"), timeout=5):
        if not slots_file.exists():
            today = date.today()
            rows = []
            number = 1
            for day_offset in (1, 2, 3):
                day = (today + timedelta(days=day_offset)).isoformat()
                for department, (doctor, times) in DOCTORS.items():
                    for hour in times:
                        rows.append({"slot_id": f"S{number:03d}", "doctor": doctor,
                                     "department": department, "date": day, "time": hour,
                                     "status": "Available", "patient_name": ""})
                        number += 1
            _atomic_write(slots_file, SLOT_FIELDS, rows)
        if not bookings_file.exists():
            _atomic_write(bookings_file, BOOKING_FIELDS, [])


def available_slots(data_dir: str | Path = "data") -> list[dict[str, str]]:
    ensure_demo_data(data_dir)
    return [row for row in _read_csv(Path(data_dir) / "doctor_slots.csv")
            if row["status"] == "Available" and row["date"] >= date.today().isoformat()]


def booked_appointments(data_dir: str | Path = "data") -> list[dict[str, str]]:
    ensure_demo_data(data_dir)
    return _read_csv(Path(data_dir) / "appointments.csv")


def book_slot(patient_name: str, department: str, appointment_date: str,
              preferred_time: str, doctor_name: str | None = None,
              data_dir: str | Path = "data") -> dict[str, str]:
    """Book only an exact, available slot; CSV changes happen under a file lock."""
    name = (patient_name or "").strip()
    department = (department or "").strip()
    day = (appointment_date or "").strip()
    hour = (preferred_time or "").strip()
    if not (2 <= len(name) <= 80):
        raise BookingError("Enter a patient name of 2 to 80 characters.")
    if department not in DEPARTMENTS:
        raise BookingError("Choose one of the listed departments.")
    try:
        selected_day = date.fromisoformat(day)
    except ValueError as exc:
        raise BookingError("Use a valid date in YYYY-MM-DD format.") from exc
    if selected_day <= date.today():
        raise BookingError("Please choose a future appointment date.")
    try:
        datetime.strptime(hour, "%H:%M")
        if not (len(hour) == 5 and hour[2] == ":"):
            raise ValueError("Time format")
    except ValueError as exc:
        raise BookingError("Use a time like 10:00 or 14:00 (24-hour clock).") from exc
    folder = Path(data_dir)
    ensure_demo_data(folder)
    with FileLock(str(folder / ".booking.lock"), timeout=5):
        slots_file = folder / "doctor_slots.csv"
        bookings_file = folder / "appointments.csv"
        slots = _read_csv(slots_file)
        match = next((r for r in slots if r["department"] == department
                      and r["date"] == day and r["time"] == hour
                      and (not doctor_name or r["doctor"].casefold() == doctor_name.strip().casefold())), None)
        if match is None:
            raise BookingError("No doctor slot exists for that department, date and time. Please choose another listed slot.")
        if match["status"] != "Available":
            raise BookingError("This slot has already been booked. Please choose another available slot.")
        match["status"] = "Booked"
        match["patient_name"] = name
        booking = {"booking_id": "APT-" + uuid.uuid4().hex[:8].upper(),
                   "slot_id": match["slot_id"], "patient_name": name,
                   "doctor": match["doctor"], "department": department,
                   "date": day, "time": hour,
                   "booked_at": datetime.now().astimezone().isoformat(timespec="seconds")}
        bookings = _read_csv(bookings_file)
        bookings.append(booking)
        _atomic_write(slots_file, SLOT_FIELDS, slots)
        _atomic_write(bookings_file, BOOKING_FIELDS, bookings)
        return booking
