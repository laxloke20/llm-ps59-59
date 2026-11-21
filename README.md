# Hospital Appointment Bot - LLM Mini Project PS59

**Roll No:** 59  
**Stack:** Python, Streamlit, Groq-hosted Llama 3.3 70B (optional Ollama), CSV storage  
**Purpose:** Fictional hospital appointment-booking demo; **no real hospital integration**.

## Problem statement

Patients may find phone-based appointment booking slow. This project accepts a free-text booking request, asks an LLM to extract patient name, department, date, preferred time and optional doctor, then checks locally stored doctor slots and books only a free matching slot.

## Workflow

`Patient message -> LLM JSON extraction -> show details for confirmation -> validate -> check doctor_slots.csv -> save booking -> appointments.csv`

**Important:** The LLM only extracts information; Python validates and books. The LLM cannot invent or directly modify slots. A human must click **Confirm**.

## Setup (Windows PowerShell)

```powershell
cd llm-ps59-hospital-bot
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` with Notepad and replace `your_groq_api_key_here` with your Groq API key. Get a key at https://console.groq.com/keys. Never commit `.env`.

```powershell
streamlit run app.py
```

Open the local address shown by Streamlit (normally http://localhost:8501).

**Ollama option (no API key):** If you already have Ollama running with a suitable installed model, set `OLLAMA_MODEL` to your model's name in `.env` and select **Ollama (local)** in the sidebar. The model must already be installed; no download is done by the app.

## Sample test inputs

Replace `{DATE}` with the future dates shown in the app's **Available doctor slots** table (normally tomorrow). Try these five prompts with the **Groq** provider:

1. `My name is Rahul Patil. Book Cardiology on {DATE} at 10 AM.` - valid slot, should book after confirmation.
2. `Book Dermatology for Neha Joshi on {DATE} at 12 noon.` - valid slot, should book after confirmation.
3. `I am Sana Khan. Need Orthopedics on {DATE} at 1 PM.` - valid slot, should book after confirmation.
4. `I am Arjun Mehta. Book Neurology on {DATE} at 10 AM.` - unsupported department; should request clarification/error.
5. `Book Cardiology for Priya Shah on {DATE} at 10 AM.` - after input 1 was booked, should reject double booking.

Extra: `Book General Medicine for Asha Patil on {DATE} at 9 AM` - valid.

Take screenshots of the analyzed request, confirmed booking, available slots, duplicate prevention and history. **Do not claim the real API has been tested until you run it with your key.**

## Run unit tests

```powershell
python -m unittest discover -s tests -v
```

Includes controlled tests for CSV slot booking, no double bookings, invalid requests, JSON validation, and a mocked Groq response. Network and live API output are **not** tested by the unit tests.

## Project structure

```text
app.py                       # Streamlit UI and confirmation step
booking.py                   # Python validation + local CSV persistence
llm_client.py                # Groq/Ollama prompt and JSON extraction
requirements.txt             # Dependencies
.env.example                 # API-key template (no real credentials)
.gitignore                   # Prevents secrets, venv and caches
sample_tests.md              # Manual test checklist
screenshots/README.txt       # How to capture the requested screenshots
report_config.json            # Fill name, class, actual GitHub URL
create_report.py              # Regenerates 2-page Report.pdf with screenshots
data/doctor_slots.csv        # Demo slots; booked rows are updated
data/appointments.csv        # Local booking log
tests/test_ps59.py           # Unit tests
```

## GitHub submission

Create a **public** repo called `llm-ps59-59` or `llm-ps59-<your-student-id>` (without checking "Add README", because this package already contains README.md), then run:

```bash
git init
git add .
git commit -m "Hospital Appointment Bot PS59"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/llm-ps59-59.git
git push -u origin main
```

Put that **actual** repository URL in `github_link.txt` and your procedure report. In your **own** class Drive folder upload `Report.pdf`, `Code.zip`, `github_link.txt`, and `screenshots/` before **22 November 2026, 11:30 AM IST**.

## Limitations and privacy

This is an educational prototype with **fictional doctors/slots**. It is not linked to any actual healthcare provider, doesn't send messages to doctors, and does not provide medical advice. Use fictitious patient names. Date/time extraction can be wrong, so review the LLM's output before confirming. For production use, add secure authentication, privacy controls, transaction-safe database storage and a real scheduling API.

## Personalize the two-page report

1. Edit `report_config.json` with your name, class and real GitHub repository URL.
2. Save genuine screenshots as `screenshots/01_booking.png` and `screenshots/02_dermatology.png` (they are automatically inserted in the report). The other 1-3 screenshots can be saved beside them.
3. Run `python create_report.py`. A personalized `Report.pdf` appears inside the project folder.
4. Check the PDF still has **exactly two A4 pages** and reflects what you actually tested, then upload it to your personal Drive folder.

The separate PDF supplied with the starter pack is a draft with blank personal details and screenshot placeholders; **do not upload it unchanged**.
