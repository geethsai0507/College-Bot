import requests
from bs4 import BeautifulSoup
import json
import re
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Faculty
from pydantic import ValidationError
from config import LOGS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOGS_DIR, 'extract_teacher.log'),
    filemode='w'
)

# 1) fetch the page
def staff(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    about = soup.find('div', id='about', class_='clearfix')
    if not about:
        logging.warning(f"Could not find the #about section in {url}")
        return []

    faculty_list = []
    for grid in about.find_all('div', class_='grid_4'):
        faculty_list.extend(process_grid(grid))

    return faculty_list


def process_grid(grid):
    faculty_list = []
    dd_blocks = grid.find_all('div', class_='dropdown') + grid.find_all('div', class_='dropdown1')
    for dd in dd_blocks:
        name_tag = dd.find('span')
        if not name_tag:
            continue

        faculty_data_raw = extract_faculty_data(dd, name_tag)
        try:
            faculty = Faculty(**faculty_data_raw)
            faculty_list.append(faculty.dict())
        except ValidationError as e:
            logging.error(f"Data validation error for {faculty_data_raw.get('name', 'Unknown')}: {e}")

    return faculty_list


def extract_faculty_data(dd, name_tag):
    f = {'name': name_tag.get_text(strip=True)}
    img = dd.find('img')
    if img and img.has_attr('src'):
        photo_src = img['src']
        if not photo_src.startswith(('http://', 'https://')):
            f['photo_url'] = f"https://nnrg.edu.in/{photo_src.lstrip('/')}"
        else:
            f['photo_url'] = photo_src
    else:
        f['photo_url'] = ''

    tbl = dd.find('table')
    if tbl:
        for tr in tbl.find_all('tr'):
            process_table_row(tr, f)
    return f


def process_table_row(tr, faculty_data):
    tds = tr.find_all('td')
    if not tds:
        return

    if tds[0].find('img'):
        raw_key = tds[1].get_text(strip=True)
        raw_val = tds[2].get_text(strip=True)
        key = raw_key.lower().replace('-', '_').replace(' ', '_')
        faculty_data[key] = raw_val
    else:
        row_txt = " ".join(td.get_text(" ", strip=True) for td in tds)
        if 'FDP' in row_txt:
            for metric, val in re.findall(r'([A-Za-z]+)\s*:\s*([\d\.]+)', row_txt):
                faculty_data[metric.lower()] = val
        elif len(tds) >= 2 and 'E-mail' in tds[0].get_text():
            email_text = tds[1].get_text(", ", strip=True)
            # Take the first email if there are multiple
            faculty_data['email'] = email_text.split(',')[0].strip()
        elif len(tds) >= 2:
            raw_key = tds[0].get_text(strip=True)
            raw_val = tds[1].get_text(strip=True)
            key = raw_key.lower().replace('-', '_').replace(' ', '_')
            faculty_data[key] = raw_val


def write_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
