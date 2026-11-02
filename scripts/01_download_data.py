"""Скачиваем Olist с Kaggle и оставляем только нужные занятию файлы."""

import hashlib
import json
import logging
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
LOGS = ROOT / 'logs'
ARCHIVE = RAW / 'olist.zip'
DOWNLOAD_URL = 'https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce'
SOURCE_PAGE = 'https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce'
FILES = {
    'olist_orders_dataset.csv': '8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf',
    'olist_order_items_dataset.csv': '0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279',
    'olist_customers_dataset.csv': '983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2',
    'olist_products_dataset.csv': '3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc',
    'product_category_name_translation.csv': 'a81f0d1f27b27e7293f761bc79e3ce8f348ee39c4b3ed3e49bde38f478586278',
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def configure_logging():
    RAW.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOGS / '01_download_data.log', mode='w', encoding='utf-8'),
        ],
    )


def files_are_ready():
    return all((RAW / name).is_file() and sha256(RAW / name) == digest
               for name, digest in FILES.items())


def download_archive():
    temporary = ARCHIVE.with_suffix('.zip.part')
    if shutil.which('curl'):
        logging.info('Скачиваем %s', DOWNLOAD_URL)
        subprocess.run([
            'curl', '--fail', '--location', '--retry', '3',
            '--progress-bar', '--output', str(temporary), DOWNLOAD_URL,
        ], check=True)
        temporary.replace(ARCHIVE)
        logging.info('Архив сохранён: %s', ARCHIVE)
        return

    # Запасной путь для систем без curl.
    request = urllib.request.Request(DOWNLOAD_URL, headers={'User-Agent': 'hse-bi-lesson/1.0'})
    logging.info('Скачиваем %s', DOWNLOAD_URL)
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open('wb') as target:
        total = int(response.headers.get('Content-Length', 0))
        downloaded = 0
        while block := response.read(1024 * 1024):
            target.write(block)
            downloaded += len(block)
            if total:
                logging.info('Получено %.1f из %.1f MB', downloaded / 2**20, total / 2**20)
    temporary.replace(ARCHIVE)
    logging.info('Архив сохранён: %s', ARCHIVE)


def extract_files():
    with zipfile.ZipFile(ARCHIVE) as archive:
        archive_names = set(archive.namelist())
        for filename in FILES:
            if filename not in archive_names:
                raise RuntimeError(f'В архиве нет {filename}')
            with archive.open(filename) as source, (RAW / filename).open('wb') as target:
                shutil.copyfileobj(source, target)
            logging.info('Извлечён %s', filename)


def write_manifest():
    manifest = {
        'dataset': 'Brazilian E-Commerce Public Dataset by Olist',
        'source_page': SOURCE_PAGE,
        'download_url': DOWNLOAD_URL,
        'retrieved': date.today().isoformat(),
        'license': 'CC BY-NC-SA 4.0 (as published on Kaggle)',
        'files': {},
    }
    for filename, expected_hash in FILES.items():
        path = RAW / filename
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise RuntimeError(f'Контрольная сумма не совпала: {filename}')
        manifest['files'][filename] = {
            'sha256': actual_hash,
            'bytes': path.stat().st_size,
        }
        logging.info('✓ %s: SHA-256 совпал', filename)

    (RAW / 'sources.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )


def main():
    configure_logging()
    if files_are_ready():
        logging.info('Все CSV уже скачаны и проверены; повторно скачивать не нужно.')
    else:
        if not ARCHIVE.exists():
            download_archive()
        extract_files()
    write_manifest()
    logging.info('Готово. Исходные данные находятся в %s', RAW)


if __name__ == '__main__':
    main()
