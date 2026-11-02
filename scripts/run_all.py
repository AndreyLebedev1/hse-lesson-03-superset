import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
STEPS = [
    '00_check_environment.py',
    '01_download_data.py',
    '02_start_database.py',
    '03_load_data.py',
    '04_check_data.py',
    '05_start_superset.py',
    '06_connect_superset.py',
    '07_status.py',
    '08_create_charts.py',
    '09_create_dashboard.py',
    '10_verify_dashboard.py',
]

for number, script in enumerate(STEPS, start=1):
    print(f'\n=== {number}/{len(STEPS)}: {script} ===\n', flush=True)
    subprocess.run([sys.executable, str(SCRIPTS / script)], check=True)

print('\nСтенд полностью готов.')
