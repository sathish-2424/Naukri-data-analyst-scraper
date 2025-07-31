import pandas as pd
import numpy as np
import logging
from collections import Counter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from config import Config

class JobMarketAnalyzer:
    def __init__(self, data=None):
        self.logger = logging.getLogger(__name__)
        self.data = data
        self.analysis_results = {}
    
    def load_data(self, df):
        """Load data for analysis"""
        self.data = df
        self.logger.info(f"Loaded {len(df) if df is not None else 0} records for analysis")
    
    def analyze_skills_demand(self):
        """Analyze skills demand across job postings"""
        if self.data is None or self.data.empty:
            return {}
        
        self.logger.info("Analyzing skills demand")
        
        # Flatten all skills
        all_skills = []
        for skills_list in self.data['skills_list'].dropna():
            if skills_list:
                all_skills.extend([skill.lower().strip() for skill in skills_list])
        
        if not all_skills:
            return {}
        
        skills_counter = Counter(all_skills)
        
        analysis = {
            'top_skills': dict(skills_counter.most_common(20)),
            'total_unique_skills': len(skills_counter),
            'skills_by_experience': self._analyze_skills_by_experience(),
            'skills_by_location': self._analyze_skills_by_location(),
            'emerging_skills': self._identify_emerging_skills()
        }
        
        self.analysis_results['skills_demand'] = analysis
        return analysis
    
    def _analyze_skills_by_experience(self):
        """Analyze skills demand by experience level"""
        skills_by_exp = {}
        
        for exp_level in self.data['experience_level'].unique():
            if pd.isna(exp_level):
                continue
                
            level_data = self.data[self.data['experience_level'] == exp_level]
            level_skills = []
            
            for skills_list in level_data['skills_list'].dropna():
                if skills_list:
                    level_skills.extend([skill.lower().strip() for skill in skills_list])
            
            if level_skills:
                skills_by_exp[exp_level] = dict(Counter(level_skills).most_common(10))
        
        return skills_by_exp
    
    def _analyze_skills_by_location(self):
        """Analyze skills demand by location"""
        skills_by_location = {}
        
        top_locations = self.data['location_cleaned'].value_counts().head(5).index
        
        for location in top_locations:
            if pd.isna(location):
                continue
                
            location_data = self.data[self.data['location_cleaned'] == location]
            location_skills = []
            
            for skills_list in location_data['skills_list'].dropna():
                if skills_list:
                    location_skills.extend([skill.lower().strip() for skill in skills_list])
            
            if location_skills:
                skills_by_location[location] = dict(Counter(location_skills).most_common(10))
        
        return skills_by_location
    
    def _identify_emerging_skills(self):
        """Identify potentially emerging skills"""
        # This is a simplified approach - in reality, you'd need historical data
        all_skills = []
        for skills_list in self.data['skills_list'].dropna():
            if skills_list:
                all_skills.extend([skill.lower().strip() for skill in skills_list])
        
        skills_counter = Counter(all_skills)
        
        # Consider skills with moderate frequency as potentially emerging
        emerging = {skill: count for skill, count in skills_counter.items() 
                   if 5 <= count <= 20}
        
        return dict(sorted(emerging.items(), key=lambda x: x[1], reverse=True))
    
    def analyze_geographic_distribution(self):
        """Analyze geographic distribution of jobs"""
        if self.data is None or self.data.empty:
            return {}
        
        self.logger.info("Analyzing geographic distribution")
        
        location_analysis = {
            'jobs_by_location': self.data['location_cleaned'].value_counts().to_dict(),
            'location_percentage': (self.data['location_cleaned'].value_counts() / len(self.data) * 100).to_dict(),
            'avg_experience_by_location': self.data.groupby('location_cleaned')['experience_min'].mean().to_dict(),
            'companies_by_location': self.data.groupby('location_cleaned')['company_cleaned'].nunique().to_dict()
        }
        
        self.analysis_results['geographic_distribution'] = location_analysis
        return location_analysis
    
    def analyze_experience_trends(self):
        """Analyze experience level trends"""
        if self.data is None or self.data.empty:
            return {}
        
        self.logger.info("Analyzing experience trends")
        
        experience_analysis = {
            'distribution': self.data['experience_level'].value_counts().to_dict(),
            'percentage': (self.data['experience_level'].value_counts() / len(self.data) * 100).to_dict(),
            'avg_min_experience': self.data['experience_min'].mean(),
            'avg_max_experience': self.data['experience_max'].mean(),
            'experience_by_location': self.data.groupby('location_cleaned')['experience_level'].value_counts().to_dict(),
            'experience_by_company_size': self._analyze_experience_by_company_size()
        }
        
        self.analysis_results['experience_trends'] = experience_analysis
        return experience_analysis
    
    def _analyze_experience_by_company_size(self):
        """Analyze experience requirements by company size (based on job postings count)"""
        company_job_counts = self.data['company_cleaned'].value_counts()
        
        # Categorize companies by number of job postings as proxy for size
        large_companies = company_job_counts[company_job_counts >= 10].index
        medium_companies = company_job_counts[(company_job_counts >= 5) & (company_job_counts < 10)].index
        small_companies = company_job_counts[company_job_counts < 5].index
        
        analysis = {}
        
        for category, companies in [('Large', large_companies), ('Medium', medium_companies), ('Small', small_companies)]:
            if len(companies) > 0:
                category_data = self.data[self.data['company_cleaned'].isin(companies)]
                analysis[category] = category_data['experience_level'].value_counts().to_dict()
        
        return analysis
    
    def analyze_company_trends(self):
        """Analyze company hiring trends"""
        if self.data is None or self.data.empty:
            return {}
        
        self.logger.info("Analyzing company trends")
        
        company_analysis = {
            'top_hiring_companies': self.data['company_cleaned'].value_counts().head(20).to_dict(),
            'companies_by_location': self.data.groupby('location_cleaned')['company_cleaned'].nunique().to_dict(),
            'avg_experience_by_company': self.data.groupby('company_cleaned')['experience_min'].mean().sort_values(ascending=False).head(10).to_dict(),
            'company_skill_preferences': self._analyze_company_skill_preferences()
        }
        
        self.analysis_results['company_trends'] = company_analysis
        return company_analysis
    
    def _analyze_company_skill_preferences(self):
        """Analyze skill preferences by top companies"""
        top_companies = self.data['company_cleaned'].value_counts().head(10).index
        company_skills = {}
        
        for company in top_companies:
            company_data = self.data[self.data['company_cleaned'] == company]
            company_skill_list = []
            
            for skills_list in company_data['skills_list'].dropna():
                if skills_list:
                    company_skill_list.extend([skill.lower().strip() for skill in skills_list])
            
            if company_skill_list:
                company_skills[company] = dict(Counter(company_skill_list).most_common(5))
        
        return company_skills
    
    def analyze_salary_trends(self):
        """Analyze salary trends"""
        if self.data is None or self.data.empty:
            return {}
        
        self.logger.info("Analyzing salary trends")
        
        salary_data = self.data.dropna(subset=['salary_min', 'salary_max'])
        
        if salary_data.empty:
            return {'message': 'No salary data available'}
        
        salary_analysis = {
            'avg_min_salary': salary_data['salary_min'].mean(),
            'avg_max_salary': salary_data['salary_max'].mean(),
            'median_min_salary': salary_data['salary_min'].median(),
            'median_max_salary': salary_data['salary_max'].median(),
            'salary_by_experience': salary_data.groupby('experience_level').agg({
                'salary_min': ['mean', 'median'],
                'salary_max': ['mean', 'median']
            }).round(2).to_dict(),
            'salary_by_location': salary_data.groupby('location_cleaned').agg({
                'salary_min': 'mean',
                'salary_max': 'mean'
            }).round(2).to_dict(),
            'salary_disclosure_rate': len(salary_data) / len(self.data) * 100
        }
        
        self.analysis_results['salary_trends'] = salary_analysis
        return salary_analysis
    
    def analyze_job_title_keywords(self):
        """Analyze keywords in job titles"""
        if self.data is None or self.data.empty:
            return {}
        
        self.logger.info("Analyzing job title keywords")
        
        # Extract keywords from job titles
        all_titles = ' '.join(self.data['job_title_cleaned'].dropna().astype(str))
        
        # Common data analyst related keywords
        keywords = ['analyst', 'data', 'business', 'senior', 'junior', 'lead', 'principal', 
                   'marketing', 'financial', 'research', 'reporting', 'insights', 'intelligence']
        
        keyword_analysis = {}
        for keyword in keywords:
            count = sum(1 for title in self.data['job_title_cleaned'].dropna() 
                       if keyword.lower() in title.lower())
            if count > 0:
                keyword_analysis[keyword] = count
        
        title_analysis = {
            'keyword_frequency': dict(sorted(keyword_analysis.items(), key=lambda x: x[1], reverse=True)),
            'title_length_stats': {
                'avg_length': self.data['job_title_cleaned'].str.len().mean(),
                'max_length': self.data['job_title_cleaned'].str.len().max(),
                'min_length': self.data['job_title_cleaned'].str.len().min()
            },
            'unique_titles': self.data['job_title_cleaned'].nunique(),
            'most_common_titles': self.data['job_title_cleaned'].value_counts().head(10).to_dict()
        }
        
        self.analysis_results['job_title_keywords'] = title_analysis
        return title_analysis
    
    def run_complete_analysis(self):
        """Run all analysis methods"""
        if self.data is None or self.data.empty:
            self.logger.error("No data available for analysis")
            return {}
        
        self.logger.info("Starting complete job market analysis")
        
        analyses = {
            'skills_demand': self.analyze_skills_demand(),
            'geographic_distribution': self.analyze_geographic_distribution(),
            'experience_trends': self.analyze_experience_trends(),
            'company_trends': self.analyze_company_trends(),
            'salary_trends': self.analyze_salary_trends(),
            'job_title_keywords': self.analyze_job_title_keywords()
        }
        
        # Add metadata
        analyses['metadata'] = {
            'analysis_date': datetime.now().isoformat(),
            'total_jobs_analyzed': len(self.data),
            'data_date_range': {
                'from': self.data['date_scraped'].min().isoformat() if 'date_scraped' in self.data else None,
                'to': self.data['date_scraped'].max().isoformat() if 'date_scraped' in self.data else None
            }
        }
        
        self.analysis_results = analyses
        self.logger.info("Complete analysis finished")
        return analyses
    
    def get_analysis_summary(self):
        """Get a summary of key insights"""
        if not self.analysis_results:
            return "No analysis results available. Run analysis first."
        
        summary = []
        
        # Top skills
        if 'skills_demand' in self.analysis_results:
            top_skills = list(self.analysis_results['skills_demand']['top_skills'].keys())[:5]
            summary.append(f"Top 5 in-demand skills: {', '.join(top_skills)}")
        
        # Top locations
        if 'geographic_distribution' in self.analysis_results:
            top_locations = list(self.analysis_results['geographic_distribution']['jobs_by_location'].keys())[:3]
            summary.append(f"Top 3 hiring locations: {', '.join(top_locations)}")
        
        # Experience distribution
        if 'experience_trends' in self.analysis_results:
            exp_dist = self.analysis_results['experience_trends']['distribution']
            most_common_exp = max(exp_dist, key=exp_dist.get)
            summary.append(f"Most common experience level: {most_common_exp}")
        
        # Top companies
        if 'company_trends' in self.analysis_results:
            top_companies = list(self.analysis_results['company_trends']['top_hiring_companies'].keys())[:3]
            summary.append(f"Top 3 hiring companies: {', '.join(top_companies)}")
        
        return '\n'.join(summary)
