"""Собираем созданные графики в один опубликованный дашборд."""

import json
import os

from superset.app import create_app


DASHBOARD_TITLE = 'Olist — динамика и структура'
DASHBOARD_SLUG = 'olist-overview'
CHART_NAMES = [
    'Olist — все заказы',
    'Olist — стоимость товаров по месяцам',
    'Olist — Top-10 категорий',
    'Olist — заказы по статусам',
]


def chart_node(chart, width, height):
    return {
        'id': f'CHART-{chart.id}',
        'type': 'CHART',
        'children': [],
        'meta': {
            'chartId': chart.id,
            'height': height,
            'width': width,
            'sliceName': chart.slice_name,
            'uuid': str(chart.uuid),
        },
        'parents': ['ROOT_ID', 'GRID_ID'],
    }


app = create_app()
with app.app_context():
    from superset import db, security_manager
    from superset.models.dashboard import Dashboard
    from superset.models.slice import Slice

    owner = security_manager.find_user(username=os.environ['SUPERSET_ADMIN_USERNAME'])
    charts = [
        db.session.query(Slice).filter_by(slice_name=name).one_or_none()
        for name in CHART_NAMES
    ]
    missing = [name for name, chart in zip(CHART_NAMES, charts) if chart is None]
    if missing:
        raise RuntimeError(f'Не найдены графики: {missing}. Сначала выполните шаг 08.')

    dashboard = db.session.query(Dashboard).filter_by(slug=DASHBOARD_SLUG).one_or_none()
    if dashboard is None:
        dashboard = Dashboard(slug=DASHBOARD_SLUG)
        db.session.add(dashboard)

    dashboard.dashboard_title = DASHBOARD_TITLE
    dashboard.description = (
        'Учебный дашборд Olist: объём заказов, динамика стоимости, категории и статусы.'
    )
    dashboard.published = True
    dashboard.owners = [owner]
    dashboard.slices = charts

    # Сетка из 12 колонок: KPI, временной ряд и два графика по половине ширины.
    positions = {
        'DASHBOARD_VERSION_KEY': 'v2',
        'ROOT_ID': {
            'id': 'ROOT_ID', 'type': 'ROOT', 'children': ['GRID_ID'],
        },
        'GRID_ID': {
            'id': 'GRID_ID', 'type': 'GRID',
            'children': ['ROW-KPI', 'ROW-TREND', 'ROW-BOTTOM'],
            'parents': ['ROOT_ID'],
        },
        'ROW-KPI': {
            'id': 'ROW-KPI', 'type': 'ROW', 'children': [f'CHART-{charts[0].id}'],
            'meta': {'background': 'BACKGROUND_TRANSPARENT'},
            'parents': ['ROOT_ID', 'GRID_ID'],
        },
        'ROW-TREND': {
            'id': 'ROW-TREND', 'type': 'ROW', 'children': [f'CHART-{charts[1].id}'],
            'meta': {'background': 'BACKGROUND_TRANSPARENT'},
            'parents': ['ROOT_ID', 'GRID_ID'],
        },
        'ROW-BOTTOM': {
            'id': 'ROW-BOTTOM', 'type': 'ROW',
            'children': [f'CHART-{charts[2].id}', f'CHART-{charts[3].id}'],
            'meta': {'background': 'BACKGROUND_TRANSPARENT'},
            'parents': ['ROOT_ID', 'GRID_ID'],
        },
    }
    for chart, width, height in [
        (charts[0], 4, 16),
        (charts[1], 12, 48),
        (charts[2], 6, 48),
        (charts[3], 6, 48),
    ]:
        positions[f'CHART-{chart.id}'] = chart_node(chart, width, height)

    dashboard.position_json = json.dumps(positions)
    dashboard.json_metadata = json.dumps({
        'color_scheme': 'supersetColors',
        'expanded_slices': {},
        'refresh_frequency': 0,
        'timed_refresh_immune_slices': [],
        'native_filter_configuration': [],
    })
    db.session.commit()

    print(json.dumps({
        'status': 'ok',
        'dashboard_id': dashboard.id,
        'title': dashboard.dashboard_title,
        'slug': dashboard.slug,
        'charts': {chart.slice_name: chart.id for chart in charts},
        'url': f'/superset/dashboard/{dashboard.slug}/',
    }, ensure_ascii=False, indent=2))

