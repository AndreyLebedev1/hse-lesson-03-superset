"""Загружаем пять исходных CSV Olist в PostgreSQL одной транзакцией."""

import csv
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg import sql


RAW = Path('/app/data/raw')
SCHEMA_SQL = Path('/app/sql/01_olist.sql')
FILES = {
    'customers': 'olist_customers_dataset.csv',
    'orders': 'olist_orders_dataset.csv',
    'order_items': 'olist_order_items_dataset.csv',
    'products': 'olist_products_dataset.csv',
    'category_translation': 'product_category_name_translation.csv',
}


def source_summary():
    manifest = json.loads((RAW / 'sources.json').read_text(encoding='utf-8'))
    counts = {}
    price_total = Decimal('0')

    for table, filename in FILES.items():
        path = RAW / filename
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        expected_hash = manifest['files'][filename]['sha256']
        if actual_hash != expected_hash:
            raise RuntimeError(f'Контрольная сумма не совпала: {filename}')

        with path.open(encoding='utf-8-sig', newline='') as source:
            reader = csv.DictReader(source)
            count = 0
            for row in reader:
                count += 1
                if table == 'order_items':
                    price_total += Decimal(row['price'])
        counts[table] = count
        print(f'Проверен {filename}: {count:,} строк')

    return counts, price_total


def ensure_reader_role(connection):
    password = os.environ['OLIST_READER_PASSWORD']
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'olist_reader'")
        if cursor.fetchone() is None:
            cursor.execute(
                sql.SQL('CREATE ROLE olist_reader LOGIN PASSWORD {}').format(sql.Literal(password))
            )
        else:
            cursor.execute(
                sql.SQL('ALTER ROLE olist_reader PASSWORD {}').format(sql.Literal(password))
            )
        cursor.execute("ALTER ROLE olist_reader SET default_transaction_read_only = on")
        cursor.execute("ALTER ROLE olist_reader SET statement_timeout = '30s'")


def load_table(cursor, table, filename, expected_count):
    path = RAW / filename
    target = sql.Identifier('raw', table)
    copy_command = sql.SQL(
        'COPY {} FROM STDIN WITH (FORMAT CSV, HEADER true)'
    ).format(target)

    print(f'Загружаем raw.{table} из {filename} ...')
    with path.open(encoding='utf-8-sig', newline='') as source:
        with cursor.copy(copy_command) as copy:
            while block := source.read(1024 * 1024):
                copy.write(block)

    cursor.execute(sql.SQL('SELECT COUNT(*) FROM {}').format(target))
    actual_count = cursor.fetchone()[0]
    if actual_count != expected_count:
        raise RuntimeError(
            f'raw.{table}: ожидалось {expected_count} строк, получено {actual_count}'
        )
    print(f'Готово: raw.{table} — {actual_count:,} строк')


def main():
    counts, expected_price = source_summary()

    # Роль создаётся на уровне сервера PostgreSQL, до основной транзакции загрузки.
    with psycopg.connect(autocommit=True) as connection:
        ensure_reader_role(connection)

    # Таблицы и представление обновляются вместе. При ошибке PostgreSQL откатит всё.
    with psycopg.connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_SQL.read_text(encoding='utf-8'))
            for table, filename in FILES.items():
                load_table(cursor, table, filename, counts[table])

            cursor.execute('SELECT COUNT(*), SUM(price) FROM analytics.olist_items')
            joined_rows, actual_price = cursor.fetchone()
            if joined_rows != counts['order_items'] or actual_price != expected_price:
                raise RuntimeError('Итоговое представление не совпало с исходными позициями')

    result = {
        'status': 'ok',
        'database': os.environ.get('PGDATABASE', 'olist'),
        'tables': counts,
        'analytics_rows': joined_rows,
        'price_total': str(actual_price),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

