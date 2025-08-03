# 📊 Data Analyst Job Market Analysis

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#)
[![License](https://img.shields.io/badge/license-Open%20Source-green.svg)](#)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](#)

> A comprehensive tool for **scraping**, **analyzing**, and **visualizing** the Data Analyst job market from job portals like **Naukri.com**.
> It provides insights into in-demand skills, job distribution, company hiring patterns, salary trends, and more.

---

## ✨ Features

* **🕷 Web Scraping**: Reliable job scraping via **Playwright**, with rate limiting & error handling.
* **🗂 Data Management**: Stores raw & processed job data in an **SQLite database**.
* **🧹 Data Processing**: Cleans duplicates, normalizes data, extracts skills & categorizes experience levels.
* **📈 Market Analysis**:

  * Skills demand (overall & segmented)
  * Geographic & experience trends
  * Company hiring & salary patterns
  * Emerging skills & job title keywords
* **📊 Visualizations**: Beautiful **matplotlib**, **seaborn**, and **Plotly** dashboards.
* **⚡ Automation**: End-to-end execution with robust logging.

---

## 🚀 Quick Start

### 1️⃣ Installation

```bash
git clone https://github.com/sathish-2424/naukri-data-analyst-scraper.git
cd naukri-data-analyst-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

📦 **Key Dependencies:** `requests`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `wordcloud`

---

### 2️⃣ Usage

The app can be run in three modes: `scrape`, `analyze`, or `full` (default):

```bash
python main.py --mode [scrape|analyze|full] --pages [num_pages] --days-back [num_days] --output-dir [output_directory] --log-level [DEBUG|INFO|WARNING|ERROR]
```

#### 🔹 Examples

* **Full Analysis (default)**

  ```bash
  python main.py
  ```
* **Scrape only, 10 pages**

  ```bash
  python main.py --mode scrape --pages 10
  ```
* **Analyze last 7 days**

  ```bash
  python main.py --mode analyze --days-back 7
  ```
* **Debug Mode**

  ```bash
  python main.py --log-level DEBUG
  ```

---

## 📂 Project Structure

```
naukri-data-analyst-scraper/
├── __pycache__/          # Compiled Python files
├── config.py             # Configurations & constants
├── scraper.py            # Web scraping logic
├── data_processor.py     # Data cleaning & processing
├── analyzer.py           # Job market analysis
├── visualizer.py         # Visualizations & dashboards
├── database.py           # SQLite operations
├── utils.py              # Helper functions
├── main.py               # Entry point
├── requirements.txt      # Project dependencies
├── data/                 # Raw & processed data
├── logs/                 # Application logs
├── debug_page_1.html     # Debugging HTML sample (1)
├── debug_page_2.html     # Debugging HTML sample (2)
├── debug_page_3.html     # Debugging HTML sample (3)
└── README.md             # Project description & usage

```

---

## ⚙️ Configuration

Modify **`config.py`** to customize:

* **Directories**: data, reports & logs paths
* **Database**: SQLite DB file path
* **Scraping**: Base URL, max pages, headers
* **Skills List & City Mapping**
* **Experience Level Ranges**

---

## 🔍 Analysis Details

The **JobMarketAnalyzer** performs:

* **Skills Demand**: top skills, emerging skills, segmented analysis
* **Geographic Trends**: jobs per city, company counts
* **Experience Trends**: average required experience by city/company
* **Company Trends**: hiring patterns & skill preferences
* **Salary Analysis**: average/median salaries, disclosure rates
* **Job Title Keywords**: common keyword frequencies

---

## 📊 Visualizations

* 📌 **Top Skills** – bar charts
* 🌍 **Location Trends** – bar & pie charts
* 🧑‍💼 **Experience Distribution** – stacked charts
* 🏢 **Top Companies** – bar charts
* ☁️ **Word Cloud** – skills visualization
* 💰 **Salary Insights** – segmented salary plots
* **Interactive Dashboard** – full Plotly dashboard (HTML)

*All plots saved in `data/reports/visualizations/`.*

---

## 🗄 Database Schema

**SQLite (`job_market.db`)** has three tables:

1. `job_postings` – job info
2. `job_skills` – extracted skills
3. `scraping_log` – scraping stats

---

## 📝 Logging

Logs are saved in:

```
logs/job_analysis_YYYYMMDD.log
```

and streamed to console using Python's `logging` module.

---

## 📜 License

This project is **open-source** and available under a standard open-source license.

---

👉 Do you also want me to **add a project banner with your repo name & tagline** at the top (like big colorful headers you see in top GitHub projects)?
Would you prefer **dark-themed badges & icons** or a **clean minimal look**?
