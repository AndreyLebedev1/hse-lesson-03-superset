"""Проверяем состав дашборда после автоматической сборки."""

import json

from superset.app import create_app


EXPECTED_CHARTS = {
    'Olist — все заказы': 'big_number_total',
    'Olist — стоимость товаров по месяцам': 'echarts_timeseries_line',
    'Olist — Top-10 категорий': 'echarts_timeseries_bar',
    'Olist — заказы по статусам': 'pie',
}


app = create_app()
with app.app_context():
    from superset import db
    from superset.models.dashboard import Dashboard

    dashboard = db.session.query(Dashboard).filter_by(slug='olist-overview').one_or_none()
    if dashboard is None:
        raise RuntimeError('Дашборд olist-overview не найден. Выполните шаг 09.')

    actual = {chart.slice_name: chart.viz_type for chart in dashboard.slices}
    if actual != EXPECTED_CHARTS:
        raise RuntimeError(f'Состав дашборда отличается: {actual}')
    if not dashboard.published:
        raise RuntimeError('Дашборд создан, но не опубликован')

    positions = json.loads(dashboard.position_json)
    chart_nodes = [key for key in positions if key.startswith('CHART-')]
    if len(chart_nodes) != len(EXPECTED_CHARTS):
        raise RuntimeError('Не все графики размещены на сетке дашборда')

    print(json.dumps({
        'status': 'ok',
        'published': dashboard.published,
        'dashboard': dashboard.dashboard_title,
        'charts': actual,
        'url': 'http://localhost:8088/superset/dashboard/olist-overview/',
    }, ensure_ascii=False, indent=2))

