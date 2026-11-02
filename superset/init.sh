#!/usr/bin/env bash
set -euo pipefail

superset db upgrade
superset init

# Команда create-admin возвращает ошибку, если пользователь уже существует.
# Сначала проверяем наличие пользователя, чтобы повторный запуск был безопасным.
python /app/lab/superset/ensure_admin.py

