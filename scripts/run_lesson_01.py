"""Урок 1: от исходных CSV до проверенной базы PostgreSQL."""

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
    '07_status.py',
]

for number, script in enumerate(STEPS, start=1):
    print(f'\n=== {number}/{len(STEPS)}: {script} ===\n', flush=True)
    subprocess.run([sys.executable, str(SCRIPTS / script)], check=True)

print('\nУрок 1 готов: данные находятся в PostgreSQL и доступны из DBeaver.')

