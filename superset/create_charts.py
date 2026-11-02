"""Идемпотентно создаём четыре учебных графика по analytics.olist_items."""

import json
import os

from superset.app import create_app


DATASET_SCHEMA = 'analytics'
DATASET_NAME = 'olist_items'


def chart_specs(datasource):
    return [
        {
            'name': 'Olist — все заказы',
            'viz_type': 'big_number_total',
            'params': {
                'viz_type': 'big_number_total',
                'datasource': datasource,
                'metric': 'orders_count',
                'adhoc_filters': [],
                'time_range': 'No filter',
                'header_font_size': 0.4,
                'subheader_font_size': 0.15,
                'y_axis_format': 'SMART_NUMBER',
            },
        },
        {
            'name': 'Olist — стоимость товаров по месяцам',
            'viz_type': 'echarts_timeseries_line',
            'params': {
                'viz_type': 'echarts_timeseries_line',
                'datasource': datasource,
                'x_axis': 'order_purchase_timestamp',
                'time_grain_sqla': 'P1M',
                'time_range': 'No filter',
                'metrics': ['revenue'],
                'groupby': [],
                'adhoc_filters': [],
                'row_limit': 10000,
                'show_legend': True,
                'rich_tooltip': True,
                'y_axis_format': 'SMART_NUMBER',
                'truncate_metric': True,
            },
        },
        {
            'name': 'Olist — Top-10 категорий',
            'viz_type': 'echarts_timeseries_bar',
            'params': {
                'viz_type': 'echarts_timeseries_bar',
                'datasource': datasource,
                'x_axis': 'product_category_name_english',
                'time_range': 'No filter',
                'metrics': ['revenue'],
                'groupby': [],
                'adhoc_filters': [],
                'row_limit': 10,
                'order_desc': True,
                'show_legend': False,
                'y_axis_format': 'SMART_NUMBER',
                'truncate_metric': True,
            },
        },
        {
            'name': 'Olist — заказы по статусам',
            'viz_type': 'pie',
            'params': {
                'viz_type': 'pie',
                'datasource': datasource,
                'groupby': ['order_status'],
                'metric': 'orders_count',
                'adhoc_filters': [],
                'time_range': 'No filter',
                'row_limit': 100,
                'sort_by_metric': True,
                'donut': False,
                'show_legend': True,
                'show_labels': True,
                'label_type': 'key_value_percent',
                'number_format': 'SMART_NUMBER',
            },
        },
    ]


app = create_app()
with app.app_context():
    from superset import db, security_manager
    from superset.connectors.sqla.models import SqlaTable
    from superset.models.slice import Slice

    owner = security_manager.find_user(username=os.environ['SUPERSET_ADMIN_USERNAME'])
    dataset = db.session.query(SqlaTable).filter_by(
        schema=DATASET_SCHEMA,
        table_name=DATASET_NAME,
    ).one_or_none()
    if dataset is None:
        raise RuntimeError('Датасет analytics.olist_items не найден. Сначала выполните шаг 06.')

    datasource = f'{dataset.id}__table'
    result = {}
    for spec in chart_specs(datasource):
        chart = db.session.query(Slice).filter_by(slice_name=spec['name']).one_or_none()
        if chart is None:
            chart = Slice(slice_name=spec['name'])
            db.session.add(chart)

        chart.datasource_id = dataset.id
        chart.datasource_type = 'table'
        chart.datasource_name = f'{DATASET_SCHEMA}.{DATASET_NAME}'
        chart.viz_type = spec['viz_type']
        chart.params = json.dumps(spec['params'], ensure_ascii=False)
        chart.description = 'Учебный график занятия 3 по исходным данным Olist.'
        chart.owners = [owner]
        db.session.flush()
        result[chart.slice_name] = {'id': chart.id, 'viz_type': chart.viz_type}
        print(f'✓ График: {chart.slice_name}')

    db.session.commit()
    print(json.dumps({'status': 'ok', 'charts': result}, ensure_ascii=False, indent=2))

