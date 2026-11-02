# Лёгкий дашборд Olist в Superset

Это краткая шпаргалка после ручного подключения базы и создания датасета по
[LESSON_02_SUPERSET.md](LESSON_02_SUPERSET.md). Все графики строятся по
analytics.olist_items. Его зерно — товарная позиция заказа, поэтому число строк
не равно числу заказов. Для заказов используйте метрику
«Заказы» = COUNT(DISTINCT order_id).

## 1. KPI «Заказы»

1. Data → Datasets → analytics.olist_items → Create chart.
2. Тип графика: Big Number.
3. Metric: «Заказы».
4. Time Column: order_purchase_timestamp.
5. Time Range: No filter.
6. Название: «Все заказы».
7. Save.

## 2. Динамика стоимости товаров

1. Создайте Time-series Line Chart.
2. Time Column: order_purchase_timestamp.
3. Time Grain: Month.
4. Metric: «Стоимость товаров».
5. Название: «Стоимость товаров по месяцам».
6. Save.

График отвечает на вопрос о движении бизнеса во времени. Последний неполный
месяц нужно интерпретировать отдельно.

## 3. Категории

1. Создайте Bar Chart.
2. Dimension: product_category_name_english.
3. Metric: «Стоимость товаров».
4. Sort descending, Row limit: 10.
5. Название: «Top-10 категорий по стоимости».
6. Save.

## 4. Собираем дашборд

1. Dashboards → + Dashboard.
2. Название: «Olist: динамика и структура».
3. Добавьте три сохранённых графика.
4. Разместите KPI сверху, временной ряд во всю ширину, категории ниже.
5. Добавьте Native Filters:
   - order_purchase_timestamp;
   - customer_state;
   - order_status.
6. Проверьте, что каждый фильтр действует на все три графика.
7. Save.

## Проверка смысла

- При выборе штата меняются все показатели.
- Число заказов считается по уникальным order_id.
- Стоимость товаров — SUM(price), без стоимости доставки.
- Данные не отфильтрованы по статусу: статус задаётся фильтром на дашборде.
