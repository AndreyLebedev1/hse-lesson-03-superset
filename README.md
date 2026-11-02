# Занятие 3: от CSV до дашборда в Superset

Здесь собран один воспроизводимый путь:

    Olist CSV → PostgreSQL → проверка → Superset → датасеты → дашборд

На компьютере нужны только:

- Python 3.10 или новее;
- запущенный Docker Desktop;
- DBeaver для просмотра PostgreSQL;
- браузер для Superset.

Python-библиотеки устанавливать на компьютер не нужно. PostgreSQL, загрузчик и
Superset работают в Docker. Каждый шаг можно запускать повторно. Вывод виден в
терминале и сохраняется в папке logs.

## Быстрый запуск

Откройте терминал в этой папке и выполните:

    python3 scripts/run_all.py

Первый запуск скачивает датасет и Docker-образы, поэтому займёт больше времени.
После завершения:

- DBeaver: localhost:5433, база olist;
- Superset: http://localhost:8088.

## Последовательный запуск для занятия

### 0. Проверяем среду

    python3 scripts/00_check_environment.py

Скрипт проверит Python и Docker и автоматически создаст локальный файл .env.

### 1. Скачиваем исходные данные

    python3 scripts/01_download_data.py

Скрипт скачивает публичный Brazilian E-Commerce Public Dataset by Olist с
Kaggle, извлекает пять CSV в data/raw и проверяет SHA-256 каждого файла.
Повторный запуск не скачивает уже проверенные данные.

### 2. Запускаем PostgreSQL

    python3 scripts/02_start_database.py

Docker скачает PostgreSQL 17, создаст контейнер и дождётся готовности базы.
Лог шага: logs/02_start_database.log.

### 3. Загружаем данные

    python3 scripts/03_load_data.py

Загрузчик:

1. сверяет CSV с контрольными суммами;
2. создаёт схемы raw и analytics;
3. загружает пять исходных таблиц одной транзакцией;
4. создаёт analytics.olist_items;
5. проверяет число строк и общую стоимость товаров.

Зерно analytics.olist_items — одна товарная позиция заказа. Это основной
датасет для дашборда. В нём нет фильтра по датам или статусам заказов.

### 4. Независимо проверяем загрузку

    python3 scripts/04_check_data.py

Проверка сравнивает с CSV каждую строку и каждое значение в PostgreSQL, а затем
проверяет аналитическое представление. Успешный результат заканчивается
сообщением status: ok.

### 5. Запускаем Superset

    python3 scripts/05_start_superset.py

На первом запуске Superset создаёт служебную базу superset_meta и пользователя
администратора. После шага интерфейс доступен по адресу:

    http://localhost:8088

Логин и пароль для локального занятия: admin / admin.

### 6. Подключаем PostgreSQL к Superset

    python3 scripts/06_connect_superset.py

Скрипт проверяет соединение и регистрирует пять исходных таблиц и
analytics.olist_items как датасеты Superset. В основной датасет также добавлены
метрики «Товарные позиции», «Заказы», «Стоимость товаров» и «Средний чек».

### 7. Проверяем состояние

    python3 scripts/07_status.py

## Подключение DBeaver

Создайте соединение PostgreSQL:

| Поле | Значение |
|---|---|
| Host | localhost |
| Port | 5433 |
| Database | olist |
| Username | olist_admin |
| Password | olist_local |

После подключения откройте Schemas. В raw лежат исходные таблицы, в analytics —
готовое представление для BI. Проверочные запросы находятся в
sql/dbeaver_checks.sql.

## Что строить в Superset

Откройте Data → Datasets → analytics.olist_items. Из него удобно собрать:

1. Big Number: метрика «Заказы»;
2. Time-series Line Chart: месяц покупки и «Стоимость товаров»;
3. Bar Chart: английская категория товара и «Стоимость товаров», Top 10;
4. Pie Chart: статус заказа и «Заказы»;
5. Native Filters: дата покупки, штат покупателя и статус заказа.

Подробный маршрут находится в DASHBOARD.md.

## Остановка

    python3 scripts/stop.py

Контейнеры остановятся, но данные PostgreSQL, пользователь, графики и дашборды
останутся в Docker volumes.

## Где искать ошибку

Сначала откройте лог соответствующего шага в logs. Затем проверьте:

    docker compose ps
    docker compose logs db
    docker compose logs superset

Частые причины:

- Docker Desktop не запущен;
- порты 5433 или 8088 заняты другим приложением;
- сеть недоступна при первом скачивании данных или образов;
- шаги запущены не по порядку.

