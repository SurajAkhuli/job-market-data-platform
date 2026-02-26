import logging
import os
from datetime import datetime

LOG_DIR = "/opt/airflow/logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"pipeline_{datetime.today().strftime('%Y_%m_%d')}.log")

def get_logger(name: str):
    logger = logging.getLogger(name)

    if logger.handlers:   # prevent duplicate handlers
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    # Console handler (important for Airflow UI logs)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger