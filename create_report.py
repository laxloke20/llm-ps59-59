"""Create the editable 2-page procedure-report template PDF for PS59."""
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Image, Table, TableStyle,
                               PageBreak, Flowable)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from pathlib import Path
import json
from xml.sax.saxutils import escape
from llm_client import SYSTEM_PROMPT

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "report_config.json").read_text(encoding="utf-8"))
OUT = ROOT / "Report.pdf"

def screenshot_or_placeholder(name: str, label: str):
    file = ROOT / "screenshots" / name
    if file.exists():
        return Image(str(file), width=238, height=111, kind="proportional")
    return ScreenPlaceholder(label)

class ScreenPlaceholder(Flowable):
    def __init__(self, label: str, width=238, height=111):
        super().__init__()
        self.label, self.width, self.height = label, width, height
    def draw(self):
        self.canv.setDash(5, 4)
        self.canv.setStrokeColor(colors.HexColor("#A0AAB4"))
        self.canv.rect(0, 0, self.width, self.height)
        self.canv.setDash()
        self.canv.setFont("Helvetica", 10)
        self.canv.setFillColor(colors.HexColor("#66717B"))
        self.canv.drawCentredString(self.width / 2, self.height / 2 + 10, self.label)
        self.canv.drawCentredString(self.width / 2, self.height / 2 - 6, "Add actual app screenshot")

styles = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=16, leading=19,
                            spaceAfter=8, textColor=colors.HexColor("#193653")),
    "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=12,
                              leading=15, spaceBefore=10, spaceAfter=5,
                              textColor=colors.HexColor("#193653")),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=12, leading=15,
                           spaceAfter=4, alignment=TA_LEFT),
    "prompt": ParagraphStyle("prompt", fontName="Helvetica", fontSize=11.6,
                             leading=14, leftIndent=6, rightIndent=6, spaceAfter=2),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=10, leading=12.5,
                            spaceAfter=4, textColor=colors.HexColor("#445461"))
}

story = []
def add(content, style="body"):
    story.append(Paragraph(content, styles[style]))

add("PROCEDURE REPORT - HOSPITAL APPOINTMENT BOT", "title")
add("<b>Problem statement no.:</b> 59 &nbsp;&nbsp;&nbsp; <b>Roll no.:</b> 59")
add("<b>Student name:</b> " + escape(CONFIG.get("student_name") or "__________________________") +
    " &nbsp;&nbsp; <b>Class:</b> " + escape(CONFIG.get("class") or "__________________"))
add("<b>GitHub:</b> " + escape(CONFIG.get("github_url") or "https://github.com/___________________________"))
add("1. Problem statement", "section")
add("Manual hospital appointments can be slow and cause scheduling errors. This classroom prototype accepts a patient's natural-language request, extracts the appointment details with an LLM, and books an available fictional doctor slot using a CSV file.")
add("2. Tools and model", "section")
add("<b>Language:</b> Python. <b>UI:</b> Streamlit. <b>LLM:</b> Llama 3.3 70B via Groq Chat Completions API (optional local Ollama). <b>Libraries:</b> requests, pandas, python-dotenv, filelock, unittest. <b>Storage:</b> CSV files.")
add("3. Procedure followed", "section")
steps = [
    "Created a Python project with app.py, llm_client.py, booking.py, requirements.txt and a data folder.",
    "Defined fictitious doctors and future appointment times in doctor_slots.csv; used appointments.csv for booking history.",
    "Designed an LLM prompt to extract patient_name, department, date, time and optional doctor_name as JSON.",
    "Implemented a Groq API client that reads its key from .env rather than embedding a secret in source code.",
    "Validated the extracted JSON and displayed it for confirmation before making any change to slot availability.",
    "Implemented exact slot matching and booking; Python marks the slot Booked and records an appointment ID.",
    "Built Streamlit controls for a patient request, LLM extraction, slot table, confirmation and booking history.",
    "Ran automated local checks of valid booking, duplicate prevention, invalid requests, JSON parsing and a mocked Groq response."
]
for i, s in enumerate(steps, 1):
    add(f"<b>{i}.</b> {escape(s)}")
add("<b>Safety:</b> The app uses fictional doctors; no real hospital is contacted. Enter made-up patient details only.", "small")
story.append(PageBreak())

add("4. Prompt used and improvement", "section")
add("<b>System prompt (core instructions):</b>")
for line in SYSTEM_PROMPT.strip().splitlines():
    if line:
        add(escape(line).replace("  ", "&nbsp;&nbsp;"), "prompt")
add("<b>User prompt template:</b> Today's date is YYYY-MM-DD. Extract the appointment details from this message: [patient request].", "small")
add("<b>Improvement:</b> A basic free-text extraction prompt was made stricter by requiring fixed JSON keys, null values for missing fields and ISO date/24-hour time formats.", "small")
add("5. Results / screenshots", "section")
add("<b>Verified:</b> 13 local automated tests passed, including CSV booking and one mocked LLM API response. <b>Pending:</b> real Groq/Ollama request and five manual UI test inputs.", "small")
t = Table([[screenshot_or_placeholder("01_booking.png", "Example 1: Extracted details"),
            screenshot_or_placeholder("02_dermatology.png", "Example 2: Confirmed booking")]], colWidths=[250,250])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0)]))
story.append(t)
add("Screenshots: app outputs captured during local manual testing (or placeholders until added).", "small")
add("6. Challenges and solutions", "section")
add("A second request for the same time could cause duplicate bookings; a slot-status check and CSV file lock prevent that. Incorrect or missing LLM JSON is rejected, and unsupported departments are not booked.")
add("7. Conclusion and future scope", "section")
add("The Python booking flow works on sample data and records local confirmations. Real LLM/UI testing with an API key remains to be completed. Future scope: connect a real hospital scheduling API and add authenticated patient accounts.")

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CDD7E0"))
    canvas.line(18*mm, 15*mm, 192*mm, 15*mm)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#65717B"))
    canvas.drawRightString(192*mm, 10*mm, f"PS59 | Page {doc.page} of 2")
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm,
                        leftMargin=18*mm, topMargin=15*mm, bottomMargin=21*mm,
                        title="PS59 Hospital Appointment Bot - Procedure Report")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
