# Дашборд Olist в Superset

Дашборд создаётся последовательно после регистрации датасетов:

    python3 scripts/08_create_charts.py
    python3 scripts/09_create_dashboard.py
    python3 scripts/10_verify_dashboard.py

Открыть результат:

    http://localhost:8088/superset/dashboard/olist-overview/

Логин и пароль: admin / admin.

## Зерно данных

Все графики строятся по analytics.olist_items. Одна строка этого Dataset —
товарная позиция заказа. Если заказ содержит три товара, order_id повторяется
три раза.

Поэтому:

- COUNT(*) считает товарные позиции;
- COUNT(DISTINCT order_id) считает заказы;
- SUM(price) считает стоимость товаров без доставки;
- SUM(freight_value) отдельно считает стоимость доставки.

## Состав дашборда

### Все заказы

Big Number показывает COUNT(DISTINCT order_id). Ожидаем около 98,7 тысячи
заказов с товарными позициями.

### Стоимость товаров по месяцам

Time-series Line Chart группирует order_purchase_timestamp по месяцу и считает
SUM(price). Последний месяц неполный, поэтому его падение нельзя автоматически
интерпретировать как падение бизнеса.

### Top-10 категорий

Bar Chart группирует строки по product_category_name_english, считает
SUM(price), сортирует категории по убыванию и оставляет десять значений.

### Заказы по статусам

Pie Chart группирует данные по order_status и использует
COUNT(DISTINCT order_id). Большинство заказов имеет статус delivered, но
исходные данные намеренно не отфильтрованы.

## Что делают скрипты

- scripts/08_create_charts.py создаёт или обновляет четыре объекта Chart;
- scripts/09_create_dashboard.py создаёт Dashboard и задаёт его сетку;
- scripts/10_verify_dashboard.py проверяет публикацию, состав и размещение;
- повторный запуск не создаёт копии объектов.

После автоматической сборки дашборд можно открыть в режиме Edit dashboard и
показать студентам, как графики перемещаются и меняют размер через интерфейс.

