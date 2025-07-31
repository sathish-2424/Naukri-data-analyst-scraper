import sqlite3
import pandas as pd
from datetime import datetime
import logging
from config import Config

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Job postings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_postings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    experience_min INTEGER,
                    experience_max INTEGER,
                    salary_min REAL,
                    salary_max REAL,
                    description TEXT,
                    date_posted DATE,
                    date_scraped DATE DEFAULT CURRENT_TIMESTAMP,
                    url TEXT,
                    job_hash TEXT UNIQUE,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Skills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER,
                    skill TEXT NOT NULL,
                    skill_category TEXT,
                    FOREIGN KEY (job_id) REFERENCES job_postings(id),
                    UNIQUE(job_id, skill)
                )
            ''')
            
            # Scraping log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pages_scraped INTEGER,
                    jobs_found INTEGER,
                    jobs_inserted INTEGER,
                    duplicates_found INTEGER,
                    errors INTEGER,
                    status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def insert_job_posting(self, job_data):
        """Insert a single job posting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO job_postings 
                (job_title, company, location, experience_min, experience_max,
                 salary_min, salary_max, description, date_posted, url, job_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data['job_title'], job_data['company'], job_data['location'],
                job_data.get('experience_min'), job_data.get('experience_max'),
                job_data.get('salary_min'), job_data.get('salary_max'),
                job_data['description'], job_data.get('date_posted'),
                job_data.get('url'), job_data['job_hash']
            ))
            
            job_id = cursor.lastrowid
            
            # Insert skills if job was inserted
            if job_id and 'skills' in job_data:
                for skill in job_data['skills']:
                    cursor.execute('''
                        INSERT OR IGNORE INTO job_skills (job_id, skill, skill_category)
                        VALUES (?, ?, ?)
                    ''', (job_id, skill['name'], skill.get('category')))
            
            conn.commit()
            conn.close()
            return job_id
            
        except Exception as e:
            self.logger.error(f"Error inserting job posting: {str(e)}")
            return None
    
    def get_job_data(self, days_back=30):
        """Retrieve job data for analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT jp.*, GROUP_CONCAT(js.skill) as skills
                FROM job_postings jp
                LEFT JOIN job_skills js ON jp.id = js.job_id
                WHERE jp.date_scraped >= date('now', '-{} days')
                AND jp.is_active = 1
                GROUP BY jp.id
            '''.format(days_back)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error retrieving job data: {str(e)}")
            return pd.DataFrame()
    
    def log_scraping_session(self, stats):
        """Log scraping session statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scraping_log 
                (pages_scraped, jobs_found, jobs_inserted, duplicates_found, errors, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                stats['pages_scraped'], stats['jobs_found'], stats['jobs_inserted'],
                stats['duplicates_found'], stats['errors'], stats['status']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging scraping session: {str(e)}")
