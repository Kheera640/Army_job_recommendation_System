import re
import pdfplumber
from dateutil import parser
import pandas as pd

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF, using OCR for image-based PDFs."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += page_text + "\n"
                else:
                    # OCR fallback for image-based page
                    pil_image = page.to_image(resolution=300).original
                    ocr_text = pytesseract.image_to_string(pil_image)
                    text += ocr_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_basic_fields(text):
    """Extract personal and professional fields using more robust regex."""
    data = {
        'name': None,
        'contact': None,
        'address': None,
        'linkedin': None,
        'rank': None,
        'service_duration': None,
        'years_of_service': None
    }
    
    # Improved regex patterns
    patterns = {
        'name': r'(?:Your Name|Name):?\s*([^\n]+)',
        'contact': r'(?:Your Contact number|Contact):?\s*([^\n]+)',
        'address': r'(?:Your Address|Address):?\s*([^\n]+)',
        'linkedin': r'(?:LinkedIn|LinkedIn Profile):?\s*([^\n]+)',
        'rank': r'(?:Rank|Military Rank):?\s*([^\n]+)',
        'service_duration': r'(?:Service Duration|Service):?\s*([^\n]+)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1).strip()
    
    # Calculate years of service
    if data['service_duration']:
        try:
            dates = re.findall(r'(\d{1,2}/\d{4}|\w+\s+\d{4})', data['service_duration'])
            if len(dates) == 2:
                start = parser.parse(dates[0])
                end = parser.parse(dates[1])
                years = (end - start).days / 365.25
                data['years_of_service'] = round(years, 1)
        except Exception as e:
            print(f"Error parsing service duration: {e}")
    
    return data

def extract_sectional_fields(text):
    """Extract multi-line fields with more flexible section detection."""
    fields = {
        'experience': None,
        'interests': None,
        'education': None,
        'skills': None
    }
    
    # More flexible section headers
    section_patterns = {
        'experience': r'(?:Work Experience|Professional Experience|Experience):?',
        'interests': r'(?:Intrests|Interests|Hobbies):?',
        'education': r'(?:Academic Qualification|Education|Qualifications):?',
        'skills': r'(?:Skills|Technical Skills|Key Skills):?'
    }
    
    # Split text into sections
    sections = {}
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        # Check if line matches a section header
        section_found = False
        for section, pattern in section_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                current_section = section
                sections[current_section] = []
                section_found = True
                break
        
        # Add content to current section
        if current_section and not section_found:
            sections[current_section].append(line.strip())
    
    # Join section content
    for section in fields:
        if section in sections:
            content = '\n'.join(sections[section])
            # Remove empty lines
            content = re.sub(r'\n\s*\n', '\n', content)
            fields[section] = content.strip()
    
    return fields

def extract_skills(text):
    """Extract skills from the text with improved detection."""
    skills = []
    
    # Try to find skills section
    skills_section = extract_sectional_fields(text).get('skills')
    if skills_section:
        # Split skills by commas, bullets, or newlines
        skills = re.split(r'[,\n•]', skills_section)
        skills = [skill.strip() for skill in skills if skill.strip()]
    else:
        # Fallback: look for common skill keywords
        skill_keywords = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'technical', 'management', 'planning', 'training', 'security',
            'logistics', 'operations', 'maintenance', 'analysis'
        ]
        for keyword in skill_keywords:
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                skills.append(keyword.capitalize())
    
    return list(set(skills))  # Remove duplicates

def extract_cv_data(pdf_path):
    """Main function to extract all fields from the resume PDF."""
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("No text extracted from PDF. Please check the file path and format.")
        return None
    
    print("=== Extracted Text Preview ===")
    print(text[:500] + "..." if len(text) > 500 else text)
    print("==============================")
    
    basic = extract_basic_fields(text)
    sections = extract_sectional_fields(text)
    skills = extract_skills(text)
    
    return {
        **basic,
        **sections,
        'skills_list': skills
    }

def save_to_database(data, db_path='resume_data.db'):
    """Save extracted data to a SQLite database."""
    if not data:
        print("No data to save.")
        return
    
    # Create DataFrame
    df = pd.DataFrame([data])
    
    # Save to SQLite database
    try:
        with pd.ExcelWriter('resume_data.xlsx') as writer:
            df.to_excel(writer, index=False)
        print("Data saved to resume_data.xlsx")
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        print("Saving to CSV instead...")
        df.to_csv('resume_data.csv', index=False)
        print("Data saved to resume_data.csv")

# Example usage
import os
# ...existing code...

if __name__ == "__main__":
    pdf_file = "C:/ml/jobrec/My_Resume.pdf"
    print(f"Checking file: {pdf_file}")
    print("Exists:", os.path.exists(pdf_file))

    extracted_data = extract_cv_data(pdf_file)

    if extracted_data:
        print("\nExtracted CV Data:\n")
        for key, value in extracted_data.items():
            if key == 'skills_list':
                print(f"Skills: {', '.join(value)}")
            else:
                print(f"{key.capitalize()}: {value}")
        
        save_to_database(extracted_data)