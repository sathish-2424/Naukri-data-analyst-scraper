from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from utils import (
    create_job_hash,
    extract_experience,
    extract_salary,
    extract_skills,
    normalize_location,
)
from config import Config
from database import DatabaseManager


class JobScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseManager()
        self.stats = {
            'pages_scraped': 0,
            'jobs_found': 0,
            'jobs_inserted': 0,
            'duplicates_found': 0,
            'errors': 0
        }
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        """Start the browser and set up page."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)  # headless=False for debugging
            context = self.browser.new_context()
            self.page = context.new_page()

            # Set user agent headers
            self.page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            })

            self.logger.info("Browser started.")
        except Exception as e:
            self.logger.error(f"Error starting the browser: {e}")
            self.stop_browser()

    def stop_browser(self):
        """Stop the browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Browser stopped.")

    def get_page_content(self, url):
        """Fetch the content of a page."""
        try:
            self.page.goto(url, timeout=60000)  # Wait up to 60 seconds for page to load
            self.page.wait_for_timeout(5000)  # Wait for 5 seconds for JS-rendered content
            return self.page.content()
        except Exception as e:
            self.logger.error(f"Page access failed for {url}: {e}")
            return ""

    def build_search_url(self, page_num=1):
        """Build URL for each search page."""
        base_search_url = f"{Config.BASE_URL}/data-analyst-jobs"
        if page_num > 1:
            return f"{base_search_url}-{page_num}"
        return base_search_url

    def parse_job_listing(self, job_element):
        """Parse the job listing data."""
        try:
            job_data = {}

            title_elem = job_element.find('a', class_='title')
            if not title_elem:
                title_elem = job_element.find('a')
            if title_elem:
                job_data['job_title'] = title_elem.get_text(strip=True)
                job_data['url'] = urljoin(Config.BASE_URL, title_elem.get('href', ''))
            else:
                return None

            company_elem = job_element.find('a', class_='subTitle')
            job_data['company'] = company_elem.get_text(strip=True) if company_elem else "Unknown"

            location_elem = job_element.find('li', class_='location')
            job_data['location'] = normalize_location(location_elem.get_text(strip=True)) if location_elem else "Unknown"

            exp_elem = job_element.find('li', class_='experience')
            if exp_elem:
                exp_text = exp_elem.get_text(strip=True)
                job_data['experience_min'], job_data['experience_max'] = extract_experience(exp_text)
            else:
                job_data['experience_min'] = job_data['experience_max'] = None

            salary_elem = job_element.find('li', class_='salary')
            if salary_elem:
                salary_text = salary_elem.get_text(strip=True)
                job_data['salary_min'], job_data['salary_max'] = extract_salary(salary_text)
            else:
                job_data['salary_min'] = job_data['salary_max'] = None

            job_data['description'] = self.get_job_description(job_data['url'])

            if job_data['description']:
                job_data['skills'] = extract_skills(job_data['description'], Config.TECHNICAL_SKILLS)

            job_data['job_hash'] = create_job_hash(
                job_data['job_title'],
                job_data.get('company', ''),
                job_data.get('location', '')
            )

            return job_data
        except Exception as e:
            self.logger.error(f"Error parsing job listing: {str(e)}")
            return None

    def get_job_description(self, job_url):
        """Get the job description from the job URL."""
        if not job_url:
            return ""
        try:
            html = self.get_page_content(job_url)
            soup = BeautifulSoup(html, 'html.parser')
            desc_selectors = [
                '.dang-inner-html', '.job-description', '.JDres', '[class*="description"]'
            ]
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    return desc_elem.get_text(strip=True)
            return ""
        except Exception as e:
            self.logger.warning(f"Could not fetch job description from {job_url}: {str(e)}")
            return ""

    def scrape_page(self, page_num):
        """Scrape the jobs from a single page."""
        try:
            url = self.build_search_url(page_num)
            self.logger.info(f"Scraping page {page_num}: {url}")

            content = self.get_page_content(url)
            soup = BeautifulSoup(content, 'html.parser')

            with open(f"debug_page_{page_num}.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            job_elements = soup.select('div.srp-jobtuple-wrapper')
            if not job_elements:
                self.logger.warning(f"No job listings found on page {page_num}")
                return []

            jobs = []
            for job_elem in job_elements:
                job_data = self.parse_job_listing(job_elem)
                if job_data:
                    jobs.append(job_data)
                    self.stats['jobs_found'] += 1

            self.stats['pages_scraped'] += 1
            return jobs

        except Exception as e:
            self.logger.error(f"Error scraping page {page_num}: {str(e)}")
            self.stats['errors'] += 1
            return []

    def save_jobs_to_database(self, jobs):
        """Save the scraped job listings to the database."""
        for job in jobs:
            try:
                job_id = self.db.insert_job_posting(job)
                if job_id:
                    self.stats['jobs_inserted'] += 1
                    self.logger.debug(f"Inserted job: {job['job_title']} at {job.get('company', 'Unknown')}")
                else:
                    self.stats['duplicates_found'] += 1
            except Exception as e:
                self.logger.error(f"Error saving job to database: {str(e)}")
                self.stats['errors'] += 1

    def scrape_all_pages(self, max_pages=None):
        """Scrape all pages up to the max_pages."""
        max_pages = max_pages or Config.MAX_PAGES
        all_jobs = []
        self.logger.info(f"Starting scrape of up to {max_pages} pages")

        self.start_browser()  # Launch the browser once here

        try:
            for page_num in range(1, max_pages + 1):
                try:
                    jobs = self.scrape_page(page_num)
                    if not jobs:
                        self.logger.info(f"No jobs found on page {page_num}, stopping")
                        break
                    self.save_jobs_to_database(jobs)
                    all_jobs.extend(jobs)
                    time.sleep(Config.DELAY_BETWEEN_REQUESTS)
                    if page_num % 5 == 0:
                        self.logger.info(f"Completed {page_num} pages, found {len(all_jobs)} jobs")
                except KeyboardInterrupt:
                    self.logger.info("Scraping interrupted by user")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error on page {page_num}: {str(e)}")
                    self.stats['errors'] += 1
                    continue
            self.stats['status'] = 'completed' if self.stats['errors'] == 0 else 'completed_with_errors'
            self.db.log_scraping_session(self.stats)
            self.logger.info(f"Scraping completed. Stats: {self.stats}")
        finally:
            self.stop_browser()  # Close the browser once at the end

        return all_jobs

    def get_scraping_stats(self):
        """Return the scraping stats."""
        return self.stats.copy()
