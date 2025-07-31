import argparse
import logging
import json
import os
from datetime import datetime
from config import Config
from utils import setup_logging
from scraper import JobScraper
from data_processor import DataProcessor
from analyzer import JobMarketAnalyzer
from visualizer import JobMarketVisualizer

def main():
    """Main function to run the job market analysis"""
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Data Analyst Job Market Analysis')
    parser.add_argument('--mode', choices=['scrape', 'analyze', 'full'], 
                       default='full', help='Mode to run the application')
    parser.add_argument('--pages', type=int, default=Config.MAX_PAGES,
                       help='Number of pages to scrape')
    parser.add_argument('--days-back', type=int, default=30,
                       help='Number of days back to analyze data')
    parser.add_argument('--output-dir', type=str, default=Config.REPORTS_DIR,
                       help='Output directory for reports')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Create directories
    Config.create_directories()
    
    # Setup logging
    setup_logging(getattr(logging, args.log_level))
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Data Analyst Job Market Analysis - Mode: {args.mode}")
    
    try:
        if args.mode in ['scrape', 'full']:
            # Scraping phase
            logger.info("Starting web scraping phase")
            scraper = JobScraper()
            scraped_jobs = scraper.scrape_all_pages(max_pages=args.pages)
            
            scraping_stats = scraper.get_scraping_stats()
            logger.info(f"Scraping completed. Stats: {scraping_stats}")
            
            if not scraped_jobs:
                logger.error("No jobs scraped. Exiting.")
                return
        
        if args.mode in ['analyze', 'full']:
            # Data processing phase
            logger.info("Starting data processing phase")
            processor = DataProcessor()
            df_clean, summary_stats, skills_analysis = processor.process_all(days_back=args.days_back)
            
            if df_clean is None or df_clean.empty:
                logger.error("No data available for analysis. Exiting.")
                return
            
            # Analysis phase
            logger.info("Starting analysis phase")
            analyzer = JobMarketAnalyzer(df_clean)
            analysis_results = analyzer.run_complete_analysis()
            
            # Visualization phase
            logger.info("Starting visualization phase")
            visualizer = JobMarketVisualizer(analysis_results)
            visualizations = visualizer.generate_all_visualizations()
            
            # Generate report
            logger.info("Generating final report")
            report_data = {
                'summary_stats': summary_stats,
                'analysis_results': analysis_results,
                'analysis_summary': analyzer.get_analysis_summary(),
                'generation_time': datetime.now().isoformat()
            }
            
            # Save report
            report_filename = f"job_market_report_{Config.get_timestamp()}.json"
            report_path = os.path.join(args.output_dir, report_filename)
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Report saved to {report_path}")
            
            # Print summary
            print("\n" + "="*80)
            print("DATA ANALYST JOB MARKET ANALYSIS - SUMMARY REPORT")
            print("="*80)
            print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Jobs Analyzed: {summary_stats['total_jobs']}")
            print(f"Unique Companies: {summary_stats['unique_companies']}")
            print(f"Unique Locations: {summary_stats['unique_locations']}")
            print(f"Data Date Range: {summary_stats['date_range']['from']} to {summary_stats['date_range']['to']}")
            print("\n" + "-"*80)
            print("KEY INSIGHTS:")
            print("-"*80)
            print(analyzer.get_analysis_summary())
            print("\n" + "-"*80)
            print("OUTPUT FILES:")
            print("-"*80)
            print(f"📊 Detailed Report: {report_path}")
            print(f"📈 Visualizations: {visualizer.output_dir}")
            print(f"📋 Interactive Dashboard: {os.path.join(visualizer.output_dir, 'interactive_dashboard.html')}")
            print("="*80)
            
        logger.info("Job market analysis completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}", exc_info=True)
        raise
    
    logger.info("Application finished")

if __name__ == "__main__":
    main()
