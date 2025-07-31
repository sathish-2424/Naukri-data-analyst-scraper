import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import os
from config import Config
import logging

class JobMarketVisualizer:
    def __init__(self, analysis_results=None):
        self.analysis_results = analysis_results or {}
        self.logger = logging.getLogger(__name__)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create output directory
        self.output_dir = os.path.join(Config.REPORTS_DIR, 'visualizations')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def plot_top_skills(self, top_n=15, save_plot=True):
        """Create bar plot of top skills"""
        if 'skills_demand' not in self.analysis_results:
            self.logger.error("Skills demand analysis not found")
            return None
        
        skills_data = self.analysis_results['skills_demand']['top_skills']
        
        # Prepare data
        skills = list(skills_data.keys())[:top_n]
        counts = list(skills_data.values())[:top_n]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(skills[::-1], counts[::-1], color=plt.cm.viridis(np.linspace(0, 1, len(skills))))
        
        # Customize plot
        ax.set_xlabel('Number of Job Postings', fontsize=12, fontweight='bold')
        ax.set_ylabel('Skills', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Most Demanded Skills for Data Analysts', fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts[::-1]):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                   str(count), va='center', ha='left', fontweight='bold')
        
        plt.tight_layout()
        
        if save_plot:
            filename = os.path.join(self.output_dir, 'top_skills.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Skills plot saved to {filename}")
        
        return fig
    
    def plot_geographic_distribution(self, save_plot=True):
        """Create visualization of geographic distribution"""
        if 'geographic_distribution' not in self.analysis_results:
            self.logger.error("Geographic distribution analysis not found")
            return None
        
        location_data = self.analysis_results['geographic_distribution']['jobs_by_location']
        
        # Prepare data (top 10 locations)
        top_locations = dict(sorted(location_data.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Create subplot with pie chart and bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_locations)))
        wedges, texts, autotexts = ax1.pie(top_locations.values(), labels=top_locations.keys(), 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('Job Distribution by Location', fontsize=14, fontweight='bold')
        
        # Bar chart
        ax2.bar(range(len(top_locations)), list(top_locations.values()), color=colors)
        ax2.set_xlabel('Location', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Jobs', fontsize=12, fontweight='bold')
        ax2.set_title('Top 10 Cities for Data Analyst Jobs', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(top_locations)))
        ax2.set_xticklabels(list(top_locations.keys()), rotation=45, ha='right')
        
        # Add value labels on bars
        for i, v in enumerate(top_locations.values()):
            ax2.text(i, v + max(top_locations.values()) * 0.01, str(v), 
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_plot:
            filename = os.path.join(self.output_dir, 'geographic_distribution.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Geographic distribution plot saved to {filename}")
        
        return fig
    
    def plot_experience_distribution(self, save_plot=True):
        """Create visualization of experience level distribution"""
        if 'experience_trends' not in self.analysis_results:
            self.logger.error("Experience trends analysis not found")
            return None
        
        exp_data = self.analysis_results['experience_trends']['distribution']
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        wedges, texts, autotexts = ax1.pie(exp_data.values(), labels=exp_data.keys(), 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('Experience Level Distribution', fontsize=14, fontweight='bold')
        
        # Bar chart
        ax2.bar(exp_data.keys(), exp_data.values(), color=colors)
        ax2.set_xlabel('Experience Level', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Jobs', fontsize=12, fontweight='bold')
        ax2.set_title('Jobs by Experience Level', fontsize=14, fontweight='bold')
        
        # Add value labels on bars
        for i, (level, count) in enumerate(exp_data.items()):
            ax2.text(i, count + max(exp_data.values()) * 0.01, str(count), 
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_plot:
            filename = os.path.join(self.output_dir, 'experience_distribution.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Experience distribution plot saved to {filename}")
        
        return fig
    
    def plot_top_companies(self, top_n=15, save_plot=True):
        """Create bar plot of top hiring companies"""
        if 'company_trends' not in self.analysis_results:
            self.logger.error("Company trends analysis not found")
            return None
        
        company_data = self.analysis_results['company_trends']['top_hiring_companies']
        
        # Prepare data
        companies = list(company_data.keys())[:top_n]
        counts = list(company_data.values())[:top_n]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(companies[::-1], counts[::-1], 
                      color=plt.cm.plasma(np.linspace(0, 1, len(companies))))
        
        # Customize plot
        ax.set_xlabel('Number of Job Postings', fontsize=12, fontweight='bold')
        ax.set_ylabel('Companies', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Companies Hiring Data Analysts', fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts[::-1]):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                   str(count), va='center', ha='left', fontweight='bold')
        
        plt.tight_layout()
        
        if save_plot:
            filename = os.path.join(self.output_dir, 'top_companies.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Top companies plot saved to {filename}")
        
        return fig
    
    def create_skills_wordcloud(self, save_plot=True):
        """Create word cloud of skills"""
        if 'skills_demand' not in self.analysis_results:
            self.logger.error("Skills demand analysis not found")
            return None
        
        skills_data = self.analysis_results['skills_demand']['top_skills']
        
        # Create WordCloud
        wordcloud = WordCloud(width=1200, height=600, 
                             background_color='white',
                             colormap='viridis',
                             max_words=100,
                             relative_scaling=0.5,
                             random_state=42).generate_from_frequencies(skills_data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Data Analyst Skills Word Cloud', fontsize=16, fontweight='bold', pad=20)
        
        if save_plot:
            filename = os.path.join(self.output_dir, 'skills_wordcloud.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Skills word cloud saved to {filename}")
        
        return fig
    
    def plot_salary_analysis(self, save_plot=True):
        """Create salary analysis plots"""
        if 'salary_trends' not in self.analysis_results:
            self.logger.error("Salary trends analysis not found")
            return None
        
        salary_data = self.analysis_results['salary_trends']
        
        if 'message' in salary_data:
            self.logger.warning("No salary data available for visualization")
            return None
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Salary Analysis for Data Analysts', fontsize=16, fontweight='bold')
        
        # Average salary by experience level
        if 'salary_by_experience' in salary_data:
            exp_salary = salary_data['salary_by_experience']
            experience_levels = list(exp_salary.keys())
            min_salaries = [exp_salary[exp]['salary_min']['mean'] for exp in experience_levels]
            max_salaries = [exp_salary[exp]['salary_max']['mean'] for exp in experience_levels]
            
            x = np.arange(len(experience_levels))
            width = 0.35
            
            axes[0, 0].bar(x - width/2, min_salaries, width, label='Min Salary', alpha=0.7)
            axes[0, 0].bar(x + width/2, max_salaries, width, label='Max Salary', alpha=0.7)
            axes[0, 0].set_xlabel('Experience Level')
            axes[0, 0].set_ylabel('Salary (LPA)')
            axes[0, 0].set_title('Average Salary by Experience Level')
            axes[0, 0].set_xticks(x)
            axes[0, 0].set_xticklabels(experience_levels)
            axes[0, 0].legend()
        
        # Salary by location (top 5)
        if 'salary_by_location' in salary_data:
            loc_salary = dict(sorted(salary_data['salary_by_location'].items(), 
                                   key=lambda x: x[1]['salary_max'], reverse=True)[:5])
            locations = list(loc_salary.keys())
            avg_salaries = [(loc_salary[loc]['salary_min'] + loc_salary[loc]['salary_max'])/2 
                           for loc in locations]
            
            axes[0, 1].bar(locations, avg_salaries, color='skyblue', alpha=0.7)
            axes[0, 1].set_xlabel('Location')
            axes[0, 1].set_ylabel('Average Salary (LPA)')
            axes[0, 1].set_title('Average Salary by Top 5 Locations')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Salary distribution summary
        summary_data = {
            'Average Min': salary_data.get('avg_min_salary', 0),
            'Average Max': salary_data.get('avg_max_salary', 0),
            'Median Min': salary_data.get('median_min_salary', 0),
            'Median Max': salary_data.get('median_max_salary', 0)
        }
        
        axes[1, 0].bar(summary_data.keys(), summary_data.values(), 
                      color=['lightcoral', 'lightblue', 'lightgreen', 'lightyellow'])
        axes[1, 0].set_ylabel('Salary (LPA)')
        axes[1, 0].set_title('Salary Statistics Summary')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Salary disclosure rate
        disclosure_rate = salary_data.get('salary_disclosure_rate', 0)
        axes[1, 1].pie([disclosure_rate, 100 - disclosure_rate], 
                      labels=['Disclosed', 'Not Disclosed'], 
                      autopct='%1.1f%%',
                      colors=['lightgreen', 'lightcoral'])
        axes[1, 1].set_title('Salary Disclosure Rate')
        
        plt.tight_layout()
        
        if save_plot:
            filename = os.path.join(self.output_dir, 'salary_analysis.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Salary analysis plot saved to {filename}")
        
        return fig
    
    def create_interactive_dashboard(self):
        """Create interactive dashboard using Plotly"""
        if not self.analysis_results:
            self.logger.error("No analysis results available for dashboard")
            return None
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Top Skills', 'Geographic Distribution', 
                           'Experience Levels', 'Top Companies',
                           'Skills by Experience', 'Salary by Location'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Top Skills
        if 'skills_demand' in self.analysis_results:
            skills_data = self.analysis_results['skills_demand']['top_skills']
            top_skills = dict(sorted(skills_data.items(), key=lambda x: x[1], reverse=True)[:10])
            
            fig.add_trace(
                go.Bar(x=list(top_skills.values()), y=list(top_skills.keys()), 
                      orientation='h', name='Skills'),
                row=1, col=1
            )
        
        # Geographic Distribution
        if 'geographic_distribution' in self.analysis_results:
            location_data = self.analysis_results['geographic_distribution']['jobs_by_location']
            top_locations = dict(sorted(location_data.items(), key=lambda x: x[1], reverse=True)[:8])
            
            fig.add_trace(
                go.Pie(labels=list(top_locations.keys()), values=list(top_locations.values()),
                      name="Locations"),
                row=1, col=2
            )
        
        # Experience Levels
        if 'experience_trends' in self.analysis_results:
            exp_data = self.analysis_results['experience_trends']['distribution']
            
            fig.add_trace(
                go.Pie(labels=list(exp_data.keys()), values=list(exp_data.values()),
                      name="Experience"),
                row=2, col=1
            )
        
        # Top Companies
        if 'company_trends' in self.analysis_results:
            company_data = self.analysis_results['company_trends']['top_hiring_companies']
            top_companies = dict(sorted(company_data.items(), key=lambda x: x[1], reverse=True)[:10])
            
            fig.add_trace(
                go.Bar(x=list(top_companies.values()), y=list(top_companies.keys()),
                      orientation='h', name='Companies'),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            showlegend=False,
            title_text="Data Analyst Job Market Dashboard",
            title_x=0.5,
            title_font_size=20
        )
        
        # Save as HTML
        filename = os.path.join(self.output_dir, 'interactive_dashboard.html')
        fig.write_html(filename)
        self.logger.info(f"Interactive dashboard saved to {filename}")
        
        return fig
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        self.logger.info("Generating all visualizations")
        
        visualizations = {}
        
        try:
            visualizations['skills'] = self.plot_top_skills()
            visualizations['geographic'] = self.plot_geographic_distribution()
            visualizations['experience'] = self.plot_experience_distribution()
            visualizations['companies'] = self.plot_top_companies()
            visualizations['wordcloud'] = self.create_skills_wordcloud()
            visualizations['salary'] = self.plot_salary_analysis()
            visualizations['dashboard'] = self.create_interactive_dashboard()
            
            plt.close('all')  # Close all matplotlib figures
            self.logger.info("All visualizations generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {str(e)}")
        
        return visualizations
