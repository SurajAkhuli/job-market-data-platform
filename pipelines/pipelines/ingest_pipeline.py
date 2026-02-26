import requests
import json
import time
import yaml
import os
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv
from airflow.sdk import Variable
from pipelines.utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()

# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path("/opt/airflow")

CONFIG_PATH = BASE_DIR / "config" / "settings.yaml"
# LOG_PATH = BASE_DIR / "logs" / "ingestion_errors.log"
BRONZE_DIR = BASE_DIR / "data" / "bronze"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

COUNTRIES = config['api']['countries']
ROLES = config["api"]["roles"]
BRONZE_PATH = config["storage"]["bronze_path"]

# APP_ID = os.getenv("APP_ID")
# APP_KEY = os.getenv("APP_KEY")
APP_ID = Variable.get("APP_ID")
APP_KEY = Variable.get("APP_KEY")

def get_today_filename():
    today = datetime.today().strftime("%Y_%m_%d")
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    return BRONZE_DIR / f"raw_jobs_{today}.json"


def fetch_jobs_by_country_role(country, role, max_pages=3):
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
            logger.info(f"Fetching {role} jobs for {country}, page {page}")

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
            logger.info(
                f"[INGEST][SUCCESS] country={country} role={role} page={page} jobs_fetched={len(data['results'])}"
            )

            time.sleep(3)

        except Exception as e:
            logger.exception(
                f"[INGEST][FAIL] country={country} role={role} page={page} error={str(e)}"
            )

    return all_jobs


def run_daily_ingestion():
    start_time = time.time()
    total_jobs = 0
    failed_requests = 0

    logger.info("Starting daily ingestion")

    all_data = {
        "ingestion_date": datetime.today().strftime("%Y-%m-%d"),
        "source": "adzuna",
        "jobs": []
    }

    for country in COUNTRIES:
        for role in ROLES:
            jobs = fetch_jobs_by_country_role(country, role, max_pages=6)
            total_jobs += len(jobs)
            all_data["jobs"].extend(jobs)

    os.makedirs(BRONZE_PATH, exist_ok=True)

    output_file = get_today_filename()

    logger.info(f"ingestion complete now saving data to {output_file}")

    # create file and put data in json format
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

    # # # # # # # run this section when our ingestion failed in halfway change manually in yaml file as per your need 
    # if os.path.exists(output_file):
    #     # Load existing data
    #     with open(output_file, "r", encoding="utf-8") as f:
    #         existing_data = json.load(f)

    #     # Append new jobs to existing ones
    #     existing_data["jobs"].extend(all_data["jobs"])

    #     # Rewrite the file (still valid JSON)
    #     with open(output_file, "w", encoding="utf-8") as f:
    #         json.dump(existing_data, f, indent=2)

    logger.info(f"[INGEST][SUMMARY] total_jobs={total_jobs}")
    logger.info(f"[INGEST][TIME] duration_sec={round(time.time() - start_time, 2)}")

if __name__ == "__main__":
    run_daily_ingestion()
