"""Общие функции для коротких сценариев занятия."""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'logs'


def ensure_env():
    env_file = ROOT / '.env'
    if not env_file.exists():
        shutil.copy2(ROOT / '.env.example', env_file)
        print('Создан .env из .env.example')


def run(command, log_name, check=True):
    """Показываем вывод команды в терминале и одновременно пишем его в лог."""
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / log_name
    printable = ' '.join(command)

    with log_path.open('w', encoding='utf-8') as log:
        header = f'[{datetime.now().isoformat(timespec="seconds")}] $ {printable}'
        print(header)
        log.write(header + '\n')

        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=os.environ.copy(),
        )
        for line in process.stdout:
            print(line, end='')
            log.write(line)
        return_code = process.wait()
        footer = f'\nКод завершения: {return_code}\nЛог: {log_path}\n'
        print(footer)
        log.write(footer)

    if check and return_code != 0:
        raise SystemExit(return_code)
    return return_code


def compose(*arguments):
    return ['docker', 'compose', *arguments]


def require_docker():
    if shutil.which('docker') is None:
        raise SystemExit('Docker не найден. Установите и запустите Docker Desktop.')
    result = subprocess.run(
        ['docker', 'info'],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise SystemExit('Docker Desktop установлен, но Docker Engine сейчас недоступен.')


def python_command(script_name):
    return [sys.executable, str(ROOT / 'scripts' / script_name)]

