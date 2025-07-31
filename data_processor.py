import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import re
from utils import categorize_experience_level
from config import Config
from database import DatabaseManager

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseManager()
    
    def load_data(self, days_back=30):
        """Load job data from database"""
        self.logger.info(f"Loading job data from last {days_back} days")
        df = self.db.get_job_data(days_back)
        
        if df.empty:
            self.logger.warning("No data found in database")
            return df
        
        self.logger.info(f"Loaded {len(df)} job postings")
        return df
    
    def clean_data(self, df):
        """Clean and preprocess the data"""
        if df.empty:
            return df
        
        self.logger.info("Starting data cleaning process")
        original_count = len(df)
        
        # Remove duplicates based on job_hash
        df = df.drop_duplicates(subset=['job_hash'])
        self.logger.info(f"Removed {original_count - len(df)} duplicate records")
        
        # Clean job titles
        df['job_title_cleaned'] = df['job_title'].apply(self._clean_job_title)
        
        # Clean company names
        df['company_cleaned'] = df['company'].apply(self._clean_company_name)
        
        # Process experience levels
        df['experience_level'] = df.apply(
            lambda row: categorize_experience_level(row['experience_min'], row['experience_max']), 
            axis=1
        )
        
        # Process locations
        df['location_cleaned'] = df['location'].fillna('Unknown')
        
        # Process skills
        df['skills_list'] = df['skills'].apply(self._process_skills)
        df['skills_count'] = df['skills_list'].apply(lambda x: len(x) if x else 0)
        
        # Add salary ranges
        df['salary_range'] = df.apply(self._create_salary_range, axis=1)
        
        # Add posting age
        df['date_scraped'] = pd.to_datetime(df['date_scraped'])
        df['days_since_posted'] = (datetime.now() - df['date_scraped']).dt.days
        
        # Remove invalid records
        df = df.dropna(subset=['job_title_cleaned', 'company_cleaned'])
        
        self.logger.info(f"Data cleaning completed. Final dataset: {len(df)} records")
        return df
    
    def _clean_job_title(self, title):
        """Clean job title"""
        if pd.isna(title):
            return None
        
        title = str(title).strip()
        title = re.sub(r'\s+', ' ', title)  # Remove extra spaces
        return title
    
    def _clean_company_name(self, company):
        """Clean company name"""
        if pd.isna(company):
            return None
        
        company = str(company).strip()
        company = re.sub(r'\s+', ' ', company)
        # Remove common suffixes
        company = re.sub(r'\s*(pvt\.?|ltd\.?|limited|inc\.?|corp\.?)?\s*$', '', company, flags=re.IGNORECASE)
        return company
    
    def _process_skills(self, skills_str):
        """Process skills string into list"""
        if pd.isna(skills_str) or not skills_str:
            return []
        
        skills = [skill.strip() for skill in str(skills_str).split(',')]
        return [skill for skill in skills if skill]
    
    def _create_salary_range(self, row):
        """Create salary range string"""
        if pd.isna(row['salary_min']) or pd.isna(row['salary_max']):
            return 'Not Disclosed'
        
        return f"₹{row['salary_min']:.1f}-{row['salary_max']:.1f} LPA"
    
    def generate_summary_stats(self, df):
        """Generate summary statistics"""
        if df.empty:
            return {}
        
        stats = {
            'total_jobs': len(df),
            'unique_companies': df['company_cleaned'].nunique(),
            'unique_locations': df['location_cleaned'].nunique(),
            'avg_experience_min': df['experience_min'].mean(),
            'avg_experience_max': df['experience_max'].mean(),
            'salary_disclosed_percentage': (df['salary_min'].notna().sum() / len(df)) * 100,
            'avg_skills_per_job': df['skills_count'].mean(),
            'top_locations': df['location_cleaned'].value_counts().head(10).to_dict(),
            'top_companies': df['company_cleaned'].value_counts().head(10).to_dict(),
            'experience_distribution': df['experience_level'].value_counts().to_dict(),
            'date_range': {
                'from': df['date_scraped'].min().strftime('%Y-%m-%d'),
                'to': df['date_scraped'].max().strftime('%Y-%m-%d')
            }
        }
        
        self.logger.info("Summary statistics generated")
        return stats
    
    def extract_skills_analysis(self, df):
        """Extract and analyze skills data"""
        if df.empty:
            return pd.DataFrame()
        
        all_skills = []
        for idx, row in df.iterrows():
            if row['skills_list']:
                for skill in row['skills_list']:
                    all_skills.append({
                        'job_id': idx,
                        'skill': skill.lower().strip(),
                        'company': row['company_cleaned'],
                        'location': row['location_cleaned'],
                        'experience_level': row['experience_level']
                    })
        
        if not all_skills:
            return pd.DataFrame()
        
        skills_df = pd.DataFrame(all_skills)
        
        # Skills frequency analysis
        skills_analysis = {
            'overall_frequency': skills_df['skill'].value_counts(),
            'by_experience_level': skills_df.groupby('experience_level')['skill'].value_counts(),
            'by_location': skills_df.groupby('location')['skill'].value_counts(),
            'skills_correlation': self._calculate_skills_correlation(skills_df)
        }
        
        return skills_analysis
    
    def _calculate_skills_correlation(self, skills_df):
        """Calculate which skills appear together frequently"""
        # Create pivot table for skills correlation
        job_skills_pivot = skills_df.pivot_table(
            index='job_id', 
            columns='skill', 
            aggfunc='size', 
            fill_value=0
        )
        
        # Calculate correlation matrix
        correlation_matrix = job_skills_pivot.corr()
        
        # Get top correlations
        correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                skill1 = correlation_matrix.columns[i]
                skill2 = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                
                if corr_value > 0.3:  # Only strong correlations
                    correlations.append({
                        'skill1': skill1,
                        'skill2': skill2,
                        'correlation': corr_value
                    })
        
        return sorted(correlations, key=lambda x: x['correlation'], reverse=True)
    
    def save_processed_data(self, df, filename_suffix=""):
        """Save processed data to CSV"""
        if df.empty:
            self.logger.warning("No data to save")
            return None
        
        timestamp = Config.get_timestamp()
        filename = f"processed_jobs_{timestamp}{filename_suffix}.csv"
        filepath = os.path.join(Config.PROCESSED_DATA_DIR, filename)
        
        df.to_csv(filepath, index=False)
        self.logger.info(f"Processed data saved to {filepath}")
        return filepath
    
    def process_all(self, days_back=30):
        """Run complete data processing pipeline"""
        self.logger.info("Starting complete data processing pipeline")
        
        # Load data
        df = self.load_data(days_back)
        if df.empty:
            return None, None, None
        
        # Clean data
        df_clean = self.clean_data(df)
        
        # Generate statistics
        summary_stats = self.generate_summary_stats(df_clean)
        
        # Extract skills analysis
        skills_analysis = self.extract_skills_analysis(df_clean)
        
        # Save processed data
        self.save_processed_data(df_clean)
        
        self.logger.info("Data processing pipeline completed")
        return df_clean, summary_stats, skills_analysis
