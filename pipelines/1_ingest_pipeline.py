import requests
import json
import time
import yaml
import os
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = BASE_DIR / "config" / "settings.yaml"
LOG_PATH = BASE_DIR / "logs" / "ingestion_errors.log"
BRONZE_DIR = BASE_DIR / "data" / "bronze"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

COUNTRIES = config['api']['countries']
ROLES = config["api"]["roles"]
BRONZE_PATH = config["storage"]["bronze_path"]

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

def get_today_filename():
    today = datetime.today().strftime("%Y_%m_%d")
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    return BRONZE_DIR / f"raw_jobs_{today}.json"


def fetch_jobs_for_country(country, role, max_pages=3):
    all_jobs = []

    for page in range(1, max_pages + 1):

        base_url = f"https://api.adzuna.com/v1/api/jobs/{country.lower()}/search/{page}"

        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "what": role,
            "results_per_page": 50   
        }

        try:
            print(f"Fetching {role} jobs for {country}, page {page}")

            response = requests.get(base_url, params=params, timeout=20)

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

            data = response.json()

            for job in data["results"]:
                all_jobs.append({
                    "job_id": job.get("id"),
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name"),
                    "city": job.get("location", {}).get("display_name"),
                    "country": country,
                    "salary_min": job.get("salary_min"),
                    "salary_max": job.get("salary_max"),
                    "salary_predicted": job.get("salary_is_predicted"),
                    "description": job.get("description"),
                    "posted_date": job.get("created"),
                    "ingestion_date": datetime.today().strftime("%Y_%m_%d")
                })

            time.sleep(3)

        except Exception as e:
            with open(LOG_PATH, "a") as log:
                log.write(f"[{datetime.now()}] ERROR {country} page {page}: {str(e)}\n")
            print(f"Error on {country} page {page}, skipping...")

    return all_jobs


def run_ingestion():
    print("Starting daily ingestion...")

    all_data = {
        "ingestion_date": datetime.today().strftime("%Y-%m-%d"),
        "source": "adzuna",
        "jobs": []
    }

    for country in COUNTRIES:
        for role in ROLES:
            jobs = fetch_jobs_for_country(country, role, max_pages=6)
            all_data["jobs"].extend(jobs)

    os.makedirs(BRONZE_PATH, exist_ok=True)

    output_file = get_today_filename()

    if os.path.exists(output_file):
        # Load existing data
        with open(output_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

        # Append new jobs to existing ones
        existing_data["jobs"].extend(all_data["jobs"])

        # Rewrite the file (still valid JSON)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)

    else:
        # First run of the day — just create file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2)

    print(f"Saved {len(all_data['jobs'])} jobs to {output_file}")

if __name__ == "__main__":
    run_ingestion()
