import json
import csv
import logging
import os
from config import LOGS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOGS_DIR, 'convert_csv.log'),
    filemode='w'
)

def extract_department(photo_url, email):
    # Try extracting department from photo_url
    if photo_url:
        parts = photo_url.split('/')
        if len(parts) > 1:
            department = parts[1]
            return department.upper()  # Convert to uppercase for consistency
    
    # Fall back to email
    if email:
        email = email.replace(',,', ',')
        emails = [e.strip() for e in email.split(',') if e.strip()]
        for e in emails:
            if '@' in e:
                domain = e.split('@')[1]
                department = domain.split('.')[0]
                return department.capitalize()
    
    # If both fail
    logging.warning(f"Invalid or missing photo_url and email: {photo_url}, {email}")
    return "UNKNOWN DEPARTMENT"

def load_and_flatten_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [item for sublist in data for item in sublist]

def collect_all_keys(flattened_data, book_columns, patent_columns):
    all_keys = set()
    for entry in flattened_data:
        all_keys.update(entry.keys())
    all_keys = {
        key for key in all_keys
        if key not in book_columns and key not in patent_columns
    }
    all_keys.update(['book', 'patents', 'department'])
    return sorted(all_keys)

def extract_books_and_patents(entry, book_columns, patent_columns):
    book_values = [
        str(entry.get(book_key)) for book_key in book_columns
        if book_key in entry and entry[book_key]
    ]
    patents_values = [
        str(entry.get(patent_key)) for patent_key in patent_columns
        if patent_key in entry and entry[patent_key]
    ]
    return '; '.join(book_values) if book_values else '', '; '.join(patents_values) if patents_values else ''

def normalize_entry(entry, book_columns, patent_columns, fieldnames):
    cleaned_entry = {}
    cleaned_entry['book'], cleaned_entry['patents'] = extract_books_and_patents(entry, book_columns, patent_columns)

    photo_url = entry.get('photo_url', '')
    email = entry.get('email', '')
    cleaned_entry['department'] = extract_department(photo_url, email)

    for key in fieldnames:
        if key in ['book', 'patents', 'department']:
            continue
        value = entry.get(key, '')
        if key == 'email' and ',' in value:
            emails = [e.strip() for e in value.split(',') if e.strip()]
            value = "; ".join(emails)
        cleaned_entry[key] = value

    return cleaned_entry

def write_csv(flattened_data, fieldnames, book_columns, patent_columns, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in flattened_data:
            cleaned_entry = normalize_entry(entry, book_columns, patent_columns, fieldnames)
            writer.writerow(cleaned_entry)

def faculty_csv(json_file='faculty_data.json', csv_file='faculty_data.csv'):
    book_columns = ['book', 'book:_1', 'books', 'books:_6']
    patent_columns = ['patent', 'patent:_1', 'patents', 'patents:2', 'patient']
    try:
        flattened_data = load_and_flatten_json(json_file)
        fieldnames = collect_all_keys(flattened_data, book_columns, patent_columns)
        write_csv(flattened_data, fieldnames, book_columns, patent_columns, csv_file)
        logging.info(f"CSV file '{csv_file}' has been created successfully.")
        return True
    except Exception as e:
        logging.error(f"Error creating CSV file: {str(e)}")
        return False

if __name__ == "__main__":
    faculty_csv()
