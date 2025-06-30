import requests
from bs4 import BeautifulSoup
import hashlib
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def preprocess_job_description(job_url):
    """
    Downloads and parses a job page to extract metadata.
    Returns structured job information: title, location, summary, etc.
    """
    try:
        # Use Selenium to get fully rendered page
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(job_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Get the fully rendered HTML
        page_source = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(page_source, "html.parser")

        # Extract basic structured info
        title = soup.title.text.strip() if soup.title else ""
        raw_text = soup.get_text(separator="\n")

        # Basic heuristics
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        combined_text = " ".join(lines)

        job_id = hashlib.md5(job_url.encode()).hexdigest()[:10]

        # Extract additional information using regex patterns
        company = extract_company(combined_text)
        location = extract_location(combined_text)
        salary = extract_salary(combined_text)
        job_type = extract_job_type(combined_text)
        experience = extract_experience(combined_text)
        skills = extract_skills(combined_text)

        return {
            "job_id": job_id,
            "url": job_url,
            "title": title,
            "company": company,
            "location": location,
            "salary": salary,
            "job_type": job_type,
            "experience": experience,
            "skills": skills,
            "summary": lines[:20],
            "raw": combined_text
        }
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to requests if Selenium fails
        try:
            response = requests.get(job_url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.text.strip() if soup.title else ""
            raw_text = soup.get_text(separator="\n")
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            combined_text = " ".join(lines)
            job_id = hashlib.md5(job_url.encode()).hexdigest()[:10]
            
            return {
                "job_id": job_id,
                "url": job_url,
                "title": title,
                "summary": lines[:20],
                "raw": combined_text
            }
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            return {"error": str(e2)}


def extract_company(text):
    """Extract company name from text"""
    patterns = [
        r'at\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+in|\s+is|\s+seeks|\s+looking|\s+hiring)',
        r'([A-Z][a-zA-Z\s&.,]+?)\s+is\s+hiring',
        r'Company:\s*([A-Z][a-zA-Z\s&.,]+)',
        r'Employer:\s*([A-Z][a-zA-Z\s&.,]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            if len(company) > 2 and len(company) < 100:
                return company
    return None


def extract_location(text):
    """Extract location from text"""
    patterns = [
        r'Location:\s*([A-Z][a-zA-Z\s,]+)',
        r'in\s+([A-Z][a-zA-Z\s,]+?)(?:\s+is|\s+seeks|\s+looking)',
        r'based\s+in\s+([A-Z][a-zA-Z\s,]+)',
        r'remote\s+(?:from\s+)?([A-Z][a-zA-Z\s,]+)',
        r'([A-Z][a-zA-Z\s,]+?)\s+\(Remote\)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            if len(location) > 2 and len(location) < 100:
                return location
    return None


def extract_salary(text):
    """Extract salary information from text"""
    patterns = [
        r'\$(\d{1,3}(?:,\d{3})*(?:-\d{1,3}(?:,\d{3})*)?)\s*(?:per\s+)?(?:year|month|hour|week)',
        r'Salary:\s*\$(\d{1,3}(?:,\d{3})*(?:-\d{1,3}(?:,\d{3})*)?)',
        r'Compensation:\s*\$(\d{1,3}(?:,\d{3})*(?:-\d{1,3}(?:,\d{3})*)?)',
        r'Pay:\s*\$(\d{1,3}(?:,\d{3})*(?:-\d{1,3}(?:,\d{3})*)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"${match.group(1)}"
    return None


def extract_job_type(text):
    """Extract job type from text"""
    job_types = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'freelance']
    text_lower = text.lower()
    
    for job_type in job_types:
        if job_type in text_lower:
            return job_type.title()
    return None


def extract_experience(text):
    """Extract experience requirements from text"""
    patterns = [
        r'(\d+)\s*(?:to\s*\d+)?\s*years?\s*experience',
        r'experience:\s*(\d+)\s*(?:to\s*\d+)?\s*years?',
        r'(entry\s*level|junior|senior|lead|principal|executive)',
        r'(intern|internship|graduate|new\s*grad)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_skills(text):
    """Extract skills from text"""
    common_skills = [
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'SQL', 'MongoDB',
        'Machine Learning', 'AI', 'Data Science', 'DevOps', 'Agile', 'Scrum'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

# example usage
job_url = "https://app.synapserecruiternetwork.com/job-page/1750452159644x262203891027542000"
result = preprocess_job_description(job_url)

print("Job ID:", result["job_id"])
print("Title:", result["title"])

if result.get("company"):
    print("Company:", result["company"])
if result.get("location"):
    print("Location:", result["location"])
if result.get("salary"):
    print("Salary:", result["salary"])
if result.get("job_type"):
    print("Job Type:", result["job_type"])
if result.get("experience"):
    print("Experience:", result["experience"])
if result.get("skills"):
    print("Skills:", ", ".join(result["skills"]))

print("Summary Preview:")
print("\n".join(result["summary"]))
