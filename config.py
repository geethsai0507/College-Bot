import os

# Project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ————— EXTRACT CONFIG —————
# URLs to process
URLS = [
    "https://nnrg.edu.in/about-us.php",
    "https://nnrg.edu.in/chairman-desk.php",
    "https://nnrg.edu.in/director-desk.php",
    "https://nnrg.edu.in/deansoe.php",
    "https://nnrg.edu.in/deansop.php",
    "https://nnrg.edu.in/deansom.php",
    "https://nnrg.edu.in/courses-offered.php",
    "https://nnrg.edu.in/admission-process.php",
    "https://nnrg.edu.in/eligibilitycriteria.php",
    "https://nnrg.edu.in/admission-fee-structure.php",
    "https://nnrg.edu.in/committees.php",
    "https://nnrg.edu.in/exam-cell.php",
    "https://nnrg.edu.in/school-of-engineering.php",
    "https://nnrg.edu.in/computer-science-and-engineering.php",
    "https://nnrg.edu.in/cse-vision-mission.php",
    "https://nnrg.edu.in/cseheadprofile.php",
    "https://nnrg.edu.in/csestaff.php",
    "https://nnrg.edu.in/electronics-and-communication-engineering.php",
    "https://nnrg.edu.in/ecevm.php",
    "https://nnrg.edu.in/eceheadprofile.php",
    "https://nnrg.edu.in/ecestaff.php",
    "https://nnrg.edu.in/mechanical-engineering.php",
    "https://nnrg.edu.in/mevm.php",
    "https://nnrg.edu.in/meheadprofile.php",
    "https://nnrg.edu.in/mestaff.php",
    "https://nnrg.edu.in/civil-engineering.php",
    "https://nnrg.edu.in/civilvm.php",
    "https://nnrg.edu.in/civilheadprofile.php",
    "https://nnrg.edu.in/civilstaff.php",
    "https://nnrg.edu.in/electrical-and-electronics-engineering.php",
    "https://nnrg.edu.in/eeevm.php",
    "https://nnrg.edu.in/eeeheadprofile.php",
    "https://nnrg.edu.in/eeestaff.php",
    "https://nnrg.edu.in/humanities-and-sciences.php",
    "https://nnrg.edu.in/hsvm.php",
    "https://nnrg.edu.in/hsheadprofile.php",
    "https://nnrg.edu.in/hsstaff.php",
    "https://nnrg.edu.in/school-of-pharmacy.php",
    "https://nnrg.edu.in/sopvm.php",
    "https://nnrg.edu.in/sopheadprofile.php",
    "https://nnrg.edu.in/sopstaff.php",
    "https://nnrg.edu.in/school-of-management-sciences.php",
    "https://nnrg.edu.in/mbavm.php",
    "https://nnrg.edu.in/mbaheadprofile.php",
    "https://nnrg.edu.in/mbastaff.php",
    "https://nnrg.edu.in/central-library.php",
    "https://nnrg.edu.in/seminar-hall.php",
    "https://nnrg.edu.in/internet-facility.php",
    "https://nnrg.edu.in/sports-and-games.php",
    "https://nnrg.edu.in/girls-hostel.php",
    "https://nnrg.edu.in/anti-ragging-cell.php",
    "https://nnrg.edu.in/transportation.php",
    "https://nnrg.edu.in/cafeteria.php",
    "https://nnrg.edu.in/national-cadet-crops.php",
    "https://nnrg.edu.in/national-service-scheme.php",
    "https://nnrg.edu.in/public-speaking-club.php",
    "https://nnrg.edu.in/women-cell.php",
    "https://nnrg.edu.in/placement-cell.php",
    "https://nnrg.edu.in/training-and-placement.php",
    "https://nnrg.edu.in/task.php",
    "https://nnrg.edu.in/contact-us.php",
    "https://nnrg.edu.in/about-hyderabad.php",
    "https://nnrg.edu.in/about-telangana.php",
]

FACULTY_URLS = [
    "https://nnrg.edu.in/mbastaff.php",
    "https://nnrg.edu.in/sopstaff.php",
    "https://nnrg.edu.in/hsstaff.php",
    "https://nnrg.edu.in/eeestaff.php",
    "https://nnrg.edu.in/civilstaff.php",
    "https://nnrg.edu.in/mestaff.php",
    "https://nnrg.edu.in/ecestaff.php",
    "https://nnrg.edu.in/csestaff.php"
]

DEPARTMENT_KEYWORDS = {
    "computer-science": "COMPUTER SCIENCE AND ENGINEERING",
    "cse": "COMPUTER SCIENCE AND ENGINEERING",
    "electronics-communication": "ELECTRONICS AND COMMUNICATION ENGINEERING",
    "ece": "ELECTRONICS AND COMMUNICATION ENGINEERING",
    "mechanical": "MECHANICAL ENGINEERING",
    "me": "MECHANICAL ENGINEERING",
    "civil": "CIVIL ENGINEERING",
    "electrical-electronics": "ELECTRICAL AND ELECTRONICS ENGINEERING",
    "eee": "ELECTRICAL AND ELECTRONICS ENGINEERING",
    "humanities-sciences": "HUMANITIES AND SCIENCES",
    "hs": "HUMANITIES AND SCIENCES",
    "sop": "SCHOOL OF PHARMACY",
    "soe": "SCHOOL OF ENGINEERING",
    "som": "SCHOOL OF MANAGEMENT SCIENCES",
    "mba": "SCHOOL OF MANAGEMENT SCIENCES",
}

# File paths
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
PDF_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "pdfs")
CSV_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "csvs")
FACULTY_JSON_PATH = os.path.join(PROJECT_ROOT, "faculty_data.json")

# ————— POPULATE DATABASE CONFIG —————
DATA_PATH         = os.path.join(PROJECT_ROOT, "data")
CSV_PATH          = os.path.join(PROJECT_ROOT, "data", "csvs", "faculty_data.csv")
FAISS_DIR         = os.path.join(PROJECT_ROOT, "faiss_ollama")
PDF_CHUNK_SIZE    = 800
PDF_CHUNK_OVERLAP = 80

# --- QUERY CONFIG ---
SPECIAL_KEYWORDS = [
    "faculty", "department", "course", "syllabus", "admission",
    "subject", "placement", "training", "dean", "chairman",
    "hod", "founder", "fee", "head", "nnrg", "college"
]
