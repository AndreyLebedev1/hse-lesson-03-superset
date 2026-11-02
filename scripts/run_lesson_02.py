"""Урок 2: запускаем Superset, но подключение и датасет создаём вручную."""

import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
STEPS = [
    '00_check_environment.py',
    '02_start_database.py',
    '05_start_superset.py',
    '07_status.py',
]

for number, script in enumerate(STEPS, start=1):
    print(f'\n=== {number}/{len(STEPS)}: {script} ===\n', flush=True)
    subprocess.run([sys.executable, str(SCRIPTS / script)], check=True)

print('\nУрок 2 готов: откройте http://localhost:8088 и продолжайте по LESSON_02_SUPERSET.md.')

