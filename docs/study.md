### Passing Parameters 
silver_task = BashOperator(
    task_id="silver",
    bash_command="""
    /opt/project/venv/bin/python \
    /opt/project/pipelines/silver/transform.py \
    --input /data/bronze \
    --output /data/silver \
    --run_date {{ ds }}
    """
)
Use {{ }} only when the value must be dynamic per run. Use Jinja when: execution date needed → {{ ds }} DAG params → {{ params.env }}
Do NOT use Jinja when: static values --env prod --batch_size 100


# assuming this written on our code 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--output")
parser.add_argument("--run_date")

args = parser.parse_args()