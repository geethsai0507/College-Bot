import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from extract_teacher import staff
from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
import csv
from convert_csv import faculty_csv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import URLS, FACULTY_URLS, DEPARTMENT_KEYWORDS, PDF_OUTPUT_DIR, CSV_OUTPUT_DIR, FACULTY_JSON_PATH, CSV_PATH, LOGS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOGS_DIR, 'extract.log'),
    filemode='w'
)

def save_to_pdf(data, filename="nnrg_named_output1.pdf"):
    # Ensure the directory exists
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    
    # Update the filename to include the directory
    filepath = os.path.join(PDF_OUTPUT_DIR, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=60)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, spaceAfter=12)
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=10, spaceAfter=6, alignment=TA_LEFT)

    elements = []

    for item in data:
        elements.append(Paragraph(item['name'], title_style))
        if isinstance(item['data'], list):
            for entry in item['data']:
                for k, v in entry.items():
                    elements.append(Paragraph(f"<b>{k}:</b> {v}", text_style))
                elements.append(Spacer(1, 6))
        else:
            elements.append(Paragraph(item['data'], text_style))

        elements.append(Spacer(1, 12))  # space between sections

    doc.build(elements)
    logging.info(f"Saved full document to {filepath}")

# URLs to process
urls = URLS
faculty_urls = FACULTY_URLS


def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        if url == "https://nnrg.edu.in/transportation.php":
            return """The campus is located at about 17 Km from Secunderabad, Koti and 10 km from Uppal Ring road on Warangal High way. Good fleet of Buses from almost all the corners of the city with well trained drivers has been provided. Transportation Fee may vary from Rs 20,000 to Rs 30,000 depends on the distance. The RTC is also running city buses at good frequency towards Ghatkesar ,Korremula and Narapally .for more detailed info visit https://nnrg.edu.in/transportation.php"""

        # Remove header/sidebar sections
        for remove_id in ['stuck_container', 'slide']:
            div = soup.find('div', id=remove_id)
            if div: div.decompose()

        return clean_text(' '.join(soup.stripped_strings))
    except Exception as e:
        logging.error(f"[ERROR] {url} -> {e}")
        return ""

def get_name_from_url(url):
    if url == "https://nnrg.edu.in/":
        return "LATEST NEWS AND EVENTS"
    path = url.split('/')[-1].replace('.php', '').lower()
    for key in sorted(DEPARTMENT_KEYWORDS, key=len, reverse=True):
        if path.startswith(key):
            suffix = path[len(key):]
            parts = [DEPARTMENT_KEYWORDS[key]]
            if suffix:
                parts.append(suffix.replace("-", " ").replace("_", " "))
            return ' '.join(parts).upper()
    return path.replace("-", " ").replace("_", " ").upper()

# MAIN EXECUTION
faculty_data = []
for url in urls:
    name = get_name_from_url(url)
    logging.info(f"Processing: {name} -> {url}")

    if url in faculty_urls:
        # Generate individual PDF directly for faculty
        try:
            data = staff(url)
            safe_filename = name.replace("/", "-").replace("\\", "-").replace(":", "-") + ".pdf"
            save_to_pdf([{"name": name, "data": data}], filename=safe_filename)
            faculty_data.append(data)
            
        except Exception as e:
            logging.error(f"Error extracting faculty from {url}: {e}")
    else:
        text = extract_text_from_url(url)
        if text:
            safe_filename = name.replace("/", "-").replace("\\", "-").replace(":", "-") + ".pdf"
            save_to_pdf([{"name": name, "data": text}], filename=safe_filename)

# Ensure the CSV directory exists
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

from json_encoder import PydanticEncoder
# Save faculty data to JSON
with open(FACULTY_JSON_PATH, 'w') as json_file:
    json.dump(faculty_data, json_file, indent=4, cls=PydanticEncoder)

# Convert JSON to CSV using the faculty_csv function
try:
    faculty_csv(FACULTY_JSON_PATH, CSV_PATH)
    logging.info(f"Successfully converted faculty data to CSV at {CSV_PATH}")
except Exception as e:
    logging.error(f"Error converting to CSV: {e}")
