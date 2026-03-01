from pathlib import Path

BASE_DIR = Path("/opt/airflow")

def ensure_data_directories():
    for folder in ["bronze", "silver", "gold"]:
        (BASE_DIR / "data" / folder).mkdir(parents=True, exist_ok=True)