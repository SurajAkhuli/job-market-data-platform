import subprocess

dates = ["2026_02_05", "2026_02_07", "2026_02_08", "2026_02_10", "2026_02_12", "2026_02_13", "2026_02_18", "2026_02_21"]

# for d in dates:
#     subprocess.Popen(["python3.11", "pipelines/2_bronze_to_silver.py", d, d])
# ########### first is parameter name and second is paramter value


for d in dates:
    subprocess.Popen(["python3.11", "pipelines/2_bronze_to_silver.py", d])    