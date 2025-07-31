import os
from datetime import datetime

class Config:
    # Project settings
    PROJECT_NAME = "Data Analyst Job Market Analysis"
    VERSION = "1.0.0"
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Database
    DATABASE_PATH = os.path.join(DATA_DIR, 'job_market.db')
    
    # Scraping settings
    BASE_URL = "https://www.naukri.com"
    SEARCH_QUERY = "data analyst"
    MAX_PAGES = 50
    DELAY_BETWEEN_REQUESTS = 2
    MAX_RETRIES = 3
    
    # Headers for requests
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    # Skills to track
    TECHNICAL_SKILLS = [
        'python', 'r', 'sql', 'mysql', 'postgresql', 'mongodb', 'nosql',
        'tableau', 'power bi', 'powerbi', 'excel', 'vba', 'sas', 'spss',
        'hadoop', 'spark', 'kafka', 'aws', 'azure', 'gcp', 'docker',
        'kubernetes', 'git', 'github', 'jupyter', 'pandas', 'numpy',
        'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'matplotlib',
        'seaborn', 'plotly', 'dashboard', 'etl', 'data warehouse',
        'business intelligence', 'machine learning', 'deep learning',
        'statistics', 'statistical analysis', 'data mining', 'data visualization'
    ]
    
    # Cities to normalize
    CITY_MAPPINGS = {
        'bengaluru': 'bangalore',
        'mumbai': 'mumbai',
        'pune': 'pune',
        'hyderabad': 'hyderabad',
        'chennai': 'chennai',
        'delhi': 'delhi',
        'gurgaon': 'gurgaon',
        'noida': 'noida',
        'kolkata': 'kolkata',
        'ahmedabad': 'ahmedabad'
    }
    
    # Experience levels
    EXPERIENCE_LEVELS = {
        'entry': (0, 2),
        'mid': (3, 7),
        'senior': (8, float('inf'))
    }
    
    @classmethod
    def create_directories(cls):
        """Create project directories if they don't exist"""
        directories = [
            cls.DATA_DIR, cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR,
            cls.REPORTS_DIR, cls.LOGS_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_timestamp(cls):
        """Get current timestamp for filenames"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    
