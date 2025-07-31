import re
import hashlib
import logging
from datetime import datetime
import time
from functools import wraps

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/job_analysis_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )

def create_job_hash(job_title, company, location):
    """Create unique hash for job posting to detect duplicates"""
    unique_string = f"{job_title.lower().strip()}{company.lower().strip()}{location.lower().strip()}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def extract_experience(text):
    """Extract experience range from text"""
    if not text:
        return None, None
    
    text = text.lower()
    
    # Pattern for "X-Y years" or "X to Y years"
    pattern1 = re.search(r'(\d+)\s*[-to]\s*(\d+)\s*year', text)
    if pattern1:
        return int(pattern1.group(1)), int(pattern1.group(2))
    
    # Pattern for "X+ years" or "X years"
    pattern2 = re.search(r'(\d+)\+?\s*year', text)
    if pattern2:
        years = int(pattern2.group(1))
        return years, years + 2 if '+' in text else years
    
    # Pattern for "fresher" or "0 years"
    if any(word in text for word in ['fresher', 'entry level', '0 year']):
        return 0, 1
    
    return None, None

def extract_salary(text):
    """Extract salary range from text"""
    if not text:
        return None, None
    
    text = text.lower()
    
    # Pattern for salary in lakhs
    lakh_pattern = re.search(r'(\d+(?:\.\d+)?)\s*[-to]\s*(\d+(?:\.\d+)?)\s*lakh', text)
    if lakh_pattern:
        return float(lakh_pattern.group(1)), float(lakh_pattern.group(2))
    
    # Pattern for salary in rupees
    rupee_pattern = re.search(r'₹\s*(\d+(?:,\d+)*)\s*[-to]\s*₹?\s*(\d+(?:,\d+)*)', text)
    if rupee_pattern:
        min_sal = float(rupee_pattern.group(1).replace(',', '')) / 100000
        max_sal = float(rupee_pattern.group(2).replace(',', '')) / 100000
        return min_sal, max_sal
    
    return None, None

def extract_skills(text, skill_list):
    """Extract skills from job description"""
    if not text:
        return []
    
    text = text.lower()
    found_skills = []
    
    for skill in skill_list:
        skill_lower = skill.lower()
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text):
            found_skills.append({
                'name': skill,
                'category': categorize_skill(skill)
            })
    
    return found_skills

def categorize_skill(skill):
    """Categorize skills into different types"""
    programming_languages = ['python', 'r', 'sql', 'vba', 'java', 'scala']
    databases = ['mysql', 'postgresql', 'mongodb', 'nosql', 'oracle']
    visualization = ['tableau', 'power bi', 'powerbi', 'matplotlib', 'seaborn', 'plotly']
    cloud = ['aws', 'azure', 'gcp', 'google cloud']
    ml_tools = ['scikit-learn', 'tensorflow', 'pytorch', 'keras']
    
    skill_lower = skill.lower()
    
    if skill_lower in programming_languages:
        return 'Programming Language'
    elif skill_lower in databases:
        return 'Database'
    elif skill_lower in visualization:
        return 'Visualization'
    elif skill_lower in cloud:
        return 'Cloud Platform'
    elif skill_lower in ml_tools:
        return 'ML/AI Tool'
    else:
        return 'Other'

def normalize_location(location):
    """Normalize location names"""
    if not location:
        return None
    
    location = location.lower().strip()
    
    # Remove common suffixes
    location = re.sub(r'\s*,\s*india$', '', location)
    location = re.sub(r'\s*,\s*in$', '', location)
    
    # Apply city mappings
    from config import Config
    for key, value in Config.CITY_MAPPINGS.items():
        if key in location:
            return value.title()
    
    return location.title()

def retry_on_failure(max_retries=3, delay=1):
    """Decorator to retry function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

def categorize_experience_level(min_exp, max_exp):
    """Categorize experience into levels"""
    if min_exp is None:
        return 'Unknown'
    
    from config import Config
    
    for level, (min_range, max_range) in Config.EXPERIENCE_LEVELS.items():
        if min_range <= min_exp <= max_range:
            return level.title()
    
    return 'Senior+'
