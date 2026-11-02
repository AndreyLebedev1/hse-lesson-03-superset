"""Добавляем PostgreSQL и шесть датасетов в уже работающий Superset."""

import json
import os
from urllib.parse import quote_plus

from sqlalchemy import text
from superset.app import create_app


DATABASE_NAME = 'Olist — занятие 3'
DATASETS = [
    ('raw', 'customers', None),
    ('raw', 'orders', 'order_purchase_timestamp'),
    ('raw', 'order_items', None),
    ('raw', 'products', None),
    ('raw', 'category_translation', None),
    ('analytics', 'olist_items', 'order_purchase_timestamp'),
]


def get_or_create_database():
    database = db.session.query(Database).filter_by(database_name=DATABASE_NAME).one_or_none()
    uri = (
        'postgresql+psycopg2://olist_reader:'
        + quote_plus(os.environ['OLIST_READER_PASSWORD'])
        + '@db:5432/olist'
    )
    if database is None:
        database = Database(database_name=DATABASE_NAME, expose_in_sqllab=True)
        db.session.add(database)
    database.set_sqlalchemy_uri(uri)
    database.expose_in_sqllab = True
    database.allow_dml = False
    db.session.flush()

    # Проверяем соединение до создания датасетов: ошибка будет понятна сразу.
    with database.get_sqla_engine() as engine:
        with engine.connect() as connection:
            value = connection.execute(text('SELECT 1')).scalar_one()
    if value != 1:
        raise RuntimeError('PostgreSQL вернул неожиданный результат проверки')
    print('✓ Superset подключился к PostgreSQL')
    return database


def get_or_create_dataset(database, schema, table_name, time_column, owner):
    dataset = db.session.query(SqlaTable).filter_by(
        database_id=database.id,
        schema=schema,
        table_name=table_name,
    ).one_or_none()

    if dataset is None:
        dataset = SqlaTable(database=database, schema=schema, table_name=table_name)
        db.session.add(dataset)
        db.session.flush()

    dataset.fetch_metadata()
    dataset.owners = [owner]
    dataset.main_dttm_col = time_column
    dataset.description = (
        'Исходные данные Olist без фильтра по датам и статусам.'
        if schema == 'raw'
        else 'Одна строка — товарная позиция заказа; готовый источник для графиков.'
    )
    print(f'✓ Датасет {schema}.{table_name}')
    return dataset


def add_metrics(dataset):
    metric_specs = [
        ('items_count', 'Товарные позиции', 'COUNT(*)'),
        ('orders_count', 'Заказы', 'COUNT(DISTINCT order_id)'),
        ('revenue', 'Стоимость товаров', 'SUM(price)'),
        ('average_check', 'Средний чек', 'SUM(price) / NULLIF(COUNT(DISTINCT order_id), 0)'),
    ]
    for name, label, expression in metric_specs:
        metric = next((item for item in dataset.metrics if item.metric_name == name), None)
        if metric is None:
            metric = SqlMetric(metric_name=name, expression=expression)
            dataset.metrics.append(metric)
        metric.verbose_name = label


app = create_app()
with app.app_context():
    # ORM-модели Superset можно импортировать только после create_app().
    from superset import db, security_manager
    from superset.connectors.sqla.models import SqlaTable, SqlMetric
    from superset.models.core import Database

    owner = security_manager.find_user(username=os.environ['SUPERSET_ADMIN_USERNAME'])
    if owner is None:
        raise RuntimeError('Администратор Superset не найден. Сначала выполните шаг 05.')

    database = get_or_create_database()
    datasets = [
        get_or_create_dataset(database, schema, table, time_column, owner)
        for schema, table, time_column in DATASETS
    ]
    add_metrics(datasets[-1])
    db.session.commit()

    print(json.dumps({
        'status': 'ok',
        'database': DATABASE_NAME,
        'database_id': database.id,
        'datasets': {
            f'{dataset.schema}.{dataset.table_name}': dataset.id
            for dataset in datasets
        },
    }, ensure_ascii=False, indent=2))
