import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch, Mock

from booking import (BookingError, DEPARTMENTS, available_slots, booked_appointments,
                     book_slot, ensure_demo_data)
from llm_client import LLMError, parse_llm_response, extraction_prompt, extract_details


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        ensure_demo_data(self.folder)
        self.day = (date.today() + timedelta(days=1)).isoformat()

    def tearDown(self):
        self.tmp.cleanup()

    def test_01_booking_works_and_updates_both_csvs(self):
        result = book_slot("Rahul Patil", "Cardiology", self.day, "10:00", data_dir=self.folder)
        self.assertTrue(result["booking_id"].startswith("APT-"))
        self.assertEqual(result["doctor"], "Dr. Riya Deshmukh")
        self.assertEqual(len(booked_appointments(self.folder)), 1)
        self.assertFalse(any(s["department"] == "Cardiology" and s["date"] == self.day
                             and s["time"] == "10:00" for s in available_slots(self.folder)))

    def test_02_double_booking_is_rejected(self):
        book_slot("Rahul Patil", "Cardiology", self.day, "10:00", data_dir=self.folder)
        with self.assertRaisesRegex(BookingError, "already been booked"):
            book_slot("Priya Shah", "Cardiology", self.day, "10:00", data_dir=self.folder)
        self.assertEqual(len(booked_appointments(self.folder)), 1)

    def test_03_invalid_department_is_rejected(self):
        with self.assertRaisesRegex(BookingError, "departments"):
            book_slot("Neha Joshi", "Neurology", self.day, "10:00", data_dir=self.folder)

    def test_04_missing_slot_is_rejected(self):
        with self.assertRaisesRegex(BookingError, "No doctor slot"):
            book_slot("Neha Joshi", "Dermatology", self.day, "10:00", data_dir=self.folder)

    def test_05_past_date_is_rejected(self):
        with self.assertRaisesRegex(BookingError, "future"):
            book_slot("Arjun Mehta", "Pediatrics", "2020-01-01", "09:00", data_dir=self.folder)

    def test_06_wrong_doctor_is_rejected(self):
        with self.assertRaisesRegex(BookingError, "No doctor slot"):
            book_slot("Arjun Mehta", "Pediatrics", self.day, "09:00",
                      "Dr. Someone Else", data_dir=self.folder)

    def test_07_slots_are_preserved_between_startups(self):
        book_slot("Anita Patil", "General Medicine", self.day, "09:00", data_dir=self.folder)
        ensure_demo_data(self.folder)
        self.assertEqual(len(booked_appointments(self.folder)), 1)


class LLMTests(unittest.TestCase):
    def test_08_json_parses_all_fields(self):
        obj = {"patient_name": "Sana", "department": "Dermatology", "date": "2026-11-22",
               "time": "12:00", "doctor_name": None}
        self.assertEqual(parse_llm_response(json.dumps(obj)), obj)

    def test_09_markdown_json_codeblock_parses(self):
        raw = '```json\n{"patient_name":"Asha","department":"Cardiology","date":null,"time":null,"doctor_name":null}\n```'
        self.assertIsNone(parse_llm_response(raw)["date"])

    def test_10_invalid_json_is_rejected(self):
        with self.assertRaises(LLMError):
            parse_llm_response("Some explanatory text instead of JSON")

    def test_11_unrecognized_department_is_rejected(self):
        with self.assertRaises(LLMError):
            parse_llm_response('{"department":"Neurology"}')

    def test_12_prompt_mentions_current_date(self):
        self.assertIn("2026-11-21", extraction_prompt("Tomorrow at 9 AM", date(2026, 11, 21)))

    @patch("llm_client.requests.post")
    @patch.dict("os.environ", {"GROQ_API_KEY": "not-a-real-key-for-unit-test"})
    def test_13_groq_integration_json_contract_with_mock_server(self, post):
        mock = Mock()
        mock.raise_for_status.return_value = None
        mock.json.return_value = {"choices": [{"message": {"content": json.dumps({
            "patient_name": "Ravi", "department": "Pediatrics",
            "date": "2026-11-22", "time": "09:00", "doctor_name": None})}}]}
        post.return_value = mock
        result = extract_details("book pediatrics for Ravi tomorrow at 9 am")
        self.assertEqual(result["patient_name"], "Ravi")
        self.assertEqual(post.call_args.kwargs["json"]["temperature"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
