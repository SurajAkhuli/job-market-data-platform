from pathlib import Path
import pandas as pd, json
import numpy as np
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
date = sys.argv[1]
filename= "raw_jobs_" + date + ".json"
path= BASE_DIR / "data" / "bronze" / filename

with open(path, 'r') as f:
    data = json.load(f)
    df = pd.DataFrame(data['jobs'])


# df['ingestion_date']= date     # plz remove this line when move to production 

df = df.drop_duplicates('job_id', keep='last')          # drop duplicates
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


filename= "jobs_cleaned_" + date + ".parquet"
path= BASE_DIR / "data" / "silver" / filename
df.to_parquet(path, engine='pyarrow', compression='snappy')


# python3.11 pipelines/bronze_to_silver.py YYYY_MM_DD