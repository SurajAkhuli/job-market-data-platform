from pathlib import Path
import pandas as pd, json
import numpy as np
import sys
from pipelines.utils.logger import get_logger
logger = get_logger(__name__)

# BASE_DIR = Path(__file__).resolve().parent.parent
# date = sys.argv[1]
def transform_bronze_to_silver(date):

    BASE_DIR = Path("/opt/airflow")
    filename= "raw_jobs_" + date + ".json"
    path= BASE_DIR / "data" / "bronze" / filename

    logger.info(f"Reading json file for the date : {date}")
    with open(path, 'r') as f:
        data = json.load(f)
        jobs_df = pd.DataFrame(data['jobs'])

    logger.info(f"[SILVER] Columns present: {list(jobs_df.columns)}")
    logger.info(f"[SILVER] Null counts:\n{jobs_df.isnull().sum()}")
    logger.info(f"[SILVER][RAW_COUNT] {len(jobs_df)}")

    # DQ - Data Quality checks starts 
    # Schema Validation
    REQUIRED_COLUMNS = {
        "job_id", "title", "company", "city", "country", "salary_min", "salary_max", "salary_predicted", "description", "posted_date", "ingestion_date"
    }
    missing_cols = REQUIRED_COLUMNS - set(jobs_df.columns)
    if missing_cols:
        logger.error(f"[DQ][SCHEMA] Missing columns: {missing_cols}")
        raise ValueError("Schema validation failed")
    
    # Null Validation (Critical Fields)
    CRITICAL_COLUMNS = ["job_id", "title", "country"]

    null_counts = jobs_df[CRITICAL_COLUMNS].isnull().sum()
    logger.info(f"[DQ][NULL_COUNTS]\n{null_counts}")

    jobs_df_valid = jobs_df.dropna(subset=CRITICAL_COLUMNS)
    jobs_df_rejected = jobs_df[
        jobs_df[CRITICAL_COLUMNS].isnull().any(axis=1)
    ]

    # Salary Validation
    invalid_salary = jobs_df_valid[
        (jobs_df_valid["salary_min"].notnull()) &
        (jobs_df_valid["salary_max"].notnull()) &
        (jobs_df_valid["salary_min"] > jobs_df_valid["salary_max"])
    ]

    logger.info(f"[DQ][INVALID_SALARY] rows={len(invalid_salary)}")

    jobs_df_valid = jobs_df_valid.drop(invalid_salary.index)
    jobs_df_rejected = pd.concat([jobs_df_rejected, invalid_salary])

    # Duplicate Handling
    dup_count = jobs_df_valid.duplicated(subset=["job_id"]).sum()
    logger.info(f"[DQ][DUPLICATES] count={dup_count}")

    jobs_df_valid = jobs_df_valid.drop_duplicates(
        subset=["job_id"], keep="last"
    )

    # Text Quality (Description)
    jobs_df_valid["description_length"] = jobs_df_valid["description"].str.len()

    short_desc = jobs_df_valid[jobs_df_valid["description_length"] < 30]

    logger.info(f"[DQ][SHORT_DESC] rows={len(short_desc)}")

    jobs_df_valid = jobs_df_valid[
        jobs_df_valid["description_length"] >= 30
    ]
    jobs_df_rejected = pd.concat([jobs_df_rejected, short_desc]) 

    # Country Validation
    VALID_COUNTRIES = {"in", "us", "au", "gb", "ca"}

    invalid_country = jobs_df_valid[
        ~jobs_df_valid["country"].str.lower().isin(VALID_COUNTRIES)
    ]

    logger.info(f"[DQ][INVALID_COUNTRY] rows={len(invalid_country)}")
    jobs_df_valid = jobs_df_valid.drop(invalid_country.index)
    jobs_df_rejected = pd.concat([jobs_df_rejected, invalid_country])

    # Summary Log
    logger.info(f"""
    [DQ][SUMMARY]
    raw_rows={len(jobs_df)}
    valid_rows={len(jobs_df_valid)}
    rejected_rows={len(jobs_df_rejected)}
    """)

    # Save Rejected Data (New Layer)
    rejected_path = BASE_DIR / "data" / "silver_rejected" / f"rejected_{date}.parquet"
    rejected_path.parent.mkdir(parents=True, exist_ok=True)

    jobs_df_rejected.to_parquet(rejected_path, engine="pyarrow")

    logger.info(f"[DQ][REJECTED_SAVED] path={rejected_path}")
    #  Data Quality checks completed now data transformation starts

    df = jobs_df_valid
    # df['ingestion_date']= date     # plz remove this line when move to production 
    df = df.drop_duplicates('job_id', keep='last')          # drop duplicates
    logger.info(f"[SILVER][DEDUPED_COUNT] {len(df)}")

    logger.info("Data Transformation & Cleaning of data started..")
    df['job_id']=df['job_id'].astype('string')         # earlier as object -> string
    df['title']=df['title'].str.lower()                # lower all alphabets of title 

    df['description'] = df['description'].str.replace("\u2026", "...")
    df['description'] = df['description'].str.replace("\u2019", "`")
    df['description'] = df['description'].str.replace("\u2013", "-")
    df['description'] = df['description'].str.replace(r"\\u[0-9a-fA-F]{4}", "", regex=True)


    df['country']= df['country'].str.lower()
    multipliers = {
        "in": 1,
        "us": 90.24,
        "au": 60.28,
        "gb":122.25,
        "ca":60.18
    }
    cols = ["salary_min", "salary_max"]
    factor = df["country"].map(multipliers).fillna(1)
    df[cols] = df[cols].mul(factor, axis=0)


    conditions =[
        df['title'].str.contains('manager') | df['title'].str.contains('senior'),
        df['title'].str.contains('data engineer'),
        df['title'].str.contains('data scientist') | df['title'].str.contains('data science'),
        df['title'].str.contains('analytics engineer'),
        df['title'].str.contains('analytics') | df['title'].str.contains('analyst'),
        df['title'].str.contains('platform'),
        df['title'].str.contains('develop'),
        df['title'].str.contains('engineer') | df['title'].str.contains('architect')
    ]
    choices=[
        'project manager',
        'data engineer', 
        'data scientist', 
        'analytics engineer', 
        'data analytics', 
        'platform engineer',
        'software developer',
        'software engineer'
    ]
    df['standardized_title']= np.select(conditions, choices, default="other")
    logger.info(f"[SILVER] Sample roles distribution:\n{df['standardized_title'].value_counts().head(5)}")
    logger.info(f"[SILVER][WRITE] path={path} rows={len(df)}")


    filename= "jobs_cleaned_" + date + ".parquet"
    path= BASE_DIR / "data" / "silver" / filename
    df.to_parquet(path, engine='pyarrow', compression='snappy')
    logger.info(f"Completed bronze_to_silver for {date}")




# python3.11 pipelines/bronze_to_silver.py YYYY_MM_DD

