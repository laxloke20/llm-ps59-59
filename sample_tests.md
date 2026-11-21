# Manual test sheet (complete after using a live LLM)

Use dates from the app. Check each result and take screenshots.

| # | Patient text | Expected behavior | Actual behavior | Screenshot filename |
|---|---|---|---|---|
| 1 | Rahul Patil, Cardiology, tomorrow, 10 AM | Extract + successful booking | [fill in] | 01_booking.png |
| 2 | Neha Joshi, Dermatology, tomorrow, noon | Extract + successful booking | [fill in] | 02_dermatology.png |
| 3 | Sana Khan, Orthopedics, tomorrow, 1 PM | Extract + successful booking | [fill in] | 03_orthopedics.png |
| 4 | Arjun Mehta, Neurology, tomorrow, 10 AM | Unsupported department / clarification | [fill in] | 04_invalid_department.png |
| 5 | Priya Shah, Cardiology, tomorrow, 10 AM (after #1) | Duplicate slot rejected | [fill in] | 05_duplicate.png |

Keep the resulting screenshots in `screenshots/`. Do not include private patient details.
