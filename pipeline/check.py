"""Независимо сверяем PostgreSQL с исходными CSV."""

import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg import sql


RAW = Path('/app/data/raw')
FILES = {
    'customers': ('olist_customers_dataset.csv', ['customer_id']),
    'orders': ('olist_orders_dataset.csv', ['order_id']),
    'order_items': ('olist_order_items_dataset.csv', ['order_id', 'order_item_id']),
    'products': ('olist_products_dataset.csv', ['product_id']),
    'category_translation': (
        'product_category_name_translation.csv',
        ['product_category_name'],
    ),
}


def values_equal(source, value):
    if source == '':
        return value is None
    if isinstance(value, datetime):
        return value == datetime.fromisoformat(source)
    if isinstance(value, (Decimal, int)):
        return Decimal(value) == Decimal(source)
    return value == source


def check_table(connection, table, filename, keys):
    with (RAW / filename).open(encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        columns = reader.fieldnames
        expected = {tuple(row[key] for key in keys): row for row in reader}

    with connection.cursor() as cursor:
        cursor.execute(sql.SQL('SELECT * FROM {}').format(sql.Identifier('raw', table)))
        database_columns = [column.name for column in cursor.description]
        if database_columns != columns:
            raise RuntimeError(f'raw.{table}: порядок или состав колонок изменился')

        seen = set()
        for record in cursor:
            actual = dict(zip(columns, record))
            key = tuple(str(actual[name]) for name in keys)
            if key not in expected or key in seen:
                raise RuntimeError(f'raw.{table}: неожиданный или повторный ключ {key}')
            for column, value in actual.items():
                if not values_equal(expected[key][column], value):
                    raise RuntimeError(f'raw.{table}: отличается {key}, колонка {column}')
            seen.add(key)

    if len(seen) != len(expected):
        raise RuntimeError(f'raw.{table}: часть строк не загрузилась')
    print(f'✓ raw.{table}: совпали все {len(seen):,} строк и все значения')
    return len(seen)


def main():
    counts = {}
    with psycopg.connect(user='olist_reader', password='olist_reader_local') as connection:
        for table, (filename, keys) in FILES.items():
            counts[table] = check_table(connection, table, filename, keys)

        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*), COUNT(DISTINCT order_id), SUM(price), '
                'MIN(order_purchase_timestamp), MAX(order_purchase_timestamp) '
                'FROM analytics.olist_items'
            )
            rows, orders, price_total, first_order, last_order = cursor.fetchone()

    if rows != counts['order_items']:
        raise RuntimeError('analytics.olist_items потеряло товарные позиции')

    print(json.dumps({
        'status': 'ok',
        'all_source_values_equal': True,
        'tables': counts,
        'analytics_rows': rows,
        'orders_with_items': orders,
        'price_total': str(price_total),
        'first_order': str(first_order),
        'last_order': str(last_order),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

