# Урок 2. От таблицы PostgreSQL до дашборда Superset

Цель урока — вручную пройти три разных уровня Superset:

    Database connection → Dataset → Charts → Dashboard

Соединение отвечает за доступ к PostgreSQL. Датасет описывает таблицу,
временную колонку и общие метрики. График задаёт один способ ответа на вопрос.
Дашборд объединяет графики и общие фильтры.

## 1. Запускаем готовую инфраструктуру

Предполагается, что первый урок уже пройден и данные загружены.

    python3 scripts/run_lesson_02.py

Откройте http://localhost:8088 и войдите:

| Поле | Значение |
|---|---|
| Username | admin |
| Password | admin |

## 2. Подключаем PostgreSQL

В Superset откройте Settings → Database Connections → + Database.

Выберите PostgreSQL и заполните соединение:

| Поле | Значение |
|---|---|
| Host | db |
| Port | 5432 |
| Database name | olist |
| Username | olist_reader |
| Password | olist_reader_local |
| Display name | Olist |

Нажмите Test Connection, затем Connect.

Здесь используются db:5432, хотя DBeaver использует localhost:5433. Superset
работает внутри Docker-сети и обращается к контейнеру по имени db. DBeaver
работает на компьютере и обращается к опубликованному порту 5433.

Если форма предлагает только SQLAlchemy URI, используйте:

    postgresql+psycopg2://olist_reader:olist_reader_local@db:5432/olist

Пользователь olist_reader имеет доступ только на чтение. BI-система не должна
случайно изменять исходные таблицы.

## 3. Добавляем датасет

Откройте Data → Datasets → + Dataset и выберите:

| Поле | Значение |
|---|---|
| Database | Olist |
| Schema | analytics |
| Table | olist_items |

Нажмите Add. Затем откройте датасет для редактирования и проверьте:

- временная колонка: order_purchase_timestamp;
- зерно: одна строка — товарная позиция заказа;
- order_id повторяется, если в заказе несколько товаров.

Поэтому COUNT(*) считает позиции, а число заказов требует
COUNT(DISTINCT order_id).

## 4. Создаём общий словарь метрик

В редакторе датасета откройте Metrics и добавьте:

| Metric key | Название | SQL expression |
|---|---|---|
| items_count | Товарные позиции | COUNT(*) |
| orders_count | Заказы | COUNT(DISTINCT order_id) |
| revenue | Стоимость товаров | SUM(price) |
| average_check | Средний чек | SUM(price) / NULLIF(COUNT(DISTINCT order_id), 0) |

Сохраните датасет. Теперь разные авторы графиков будут одинаково считать
заказы и стоимость товаров.

## 5. График 1: число заказов

1. Data → Datasets → analytics.olist_items → Create chart.
2. Visualization: Big Number.
3. Metric: Заказы.
4. Time Column: order_purchase_timestamp.
5. Time Range: No filter.
6. Название: Все заказы.
7. Save.

Ожидаем около 98 666 заказов с товарными позициями.

## 6. График 2: стоимость товаров по месяцам

1. Создайте Time-series Line Chart по тому же датасету.
2. Time Column: order_purchase_timestamp.
3. Time Grain: Month.
4. Metric: Стоимость товаров.
5. Time Range: No filter.
6. Название: Стоимость товаров по месяцам.
7. Save.

Последний месяц неполный. Падение в нём нельзя автоматически трактовать как
падение бизнеса.

## 7. График 3: категории

1. Создайте Bar Chart.
2. Dimension: product_category_name_english.
3. Metric: Стоимость товаров.
4. Sort descending.
5. Row limit: 10.
6. Название: Top-10 категорий по стоимости.
7. Save.

## 8. Собираем дашборд

1. Dashboards → + Dashboard.
2. Название: Olist: динамика и структура.
3. Добавьте три сохранённых графика.
4. Разместите KPI сверху, временной ряд по ширине, категории ниже.
5. Добавьте Native Filters:
   - order_purchase_timestamp;
   - customer_state;
   - order_status.
6. Убедитесь, что фильтры применяются ко всем графикам.
7. Сохраните дашборд.

## 9. Проверяем смысл

- Заказы считаются по уникальным order_id, а не по строкам.
- Стоимость товаров равна SUM(price) и не включает доставку.
- В исходном датасете сохранены все статусы заказов.
- Выбор штата или статуса изменяет все три графика.
- Неполный последний период не сравнивается с полным предыдущим периодом.

## Запасной автоматический путь

Если ручная настройка сорвалась и нужно быстро продолжить занятие:

    python3 scripts/06_connect_superset.py

Скрипт автоматически создаст соединение, шесть датасетов и основные метрики.

