# Занятие 3: PostgreSQL и Apache Superset

Материал разделён на два урока по 80 минут:

1. CSV → PostgreSQL → проверка → DBeaver;
2. PostgreSQL → Superset Dataset → Charts → Dashboard.

На компьютере нужны Python 3.10+, Docker Desktop, DBeaver и браузер. Все
Python-зависимости находятся внутри контейнеров.

## Подготовка

    git clone https://github.com/AndreyLebedev1/hse-lesson-03-superset.git
    cd hse-lesson-03-superset

## Урок 1: создаём базу данных

Полный маршрут описан в [LESSON_01_DATABASE.md](LESSON_01_DATABASE.md).

Запуск всех технических шагов первого урока:

    python3 scripts/run_lesson_01.py

Сценарий:

1. проверяет Python и Docker;
2. скачивает публичный датасет Olist;
3. проверяет SHA-256 пяти CSV;
4. запускает PostgreSQL 17;
5. загружает исходные таблицы в схему raw;
6. создаёт analytics.olist_items;
7. сравнивает с CSV каждую строку и каждое значение.

Подключение DBeaver:

| Поле | Значение |
|---|---|
| Host | localhost |
| Port | 5433 |
| Database | olist |
| Username | olist_admin |
| Password | olist_local |

Проверочные запросы находятся в [sql/dbeaver_checks.sql](sql/dbeaver_checks.sql).

## Урок 2: создаём датасет и дашборд

Полный маршрут описан в [LESSON_02_SUPERSET.md](LESSON_02_SUPERSET.md).

Подготовка инфраструктуры второго урока:

    python3 scripts/run_lesson_02.py

Затем откройте http://localhost:8088 и войдите как admin / admin.

На втором уроке мы вручную:

1. подключим PostgreSQL к Superset;
2. добавим analytics.olist_items как Dataset;
3. определим общие метрики заказов и стоимости;
4. построим Big Number, временной ряд и Top-10 категорий;
5. объединим графики в дашборд с фильтрами.

Superset подключается к адресу db:5432, потому что работает внутри Docker-сети.
DBeaver подключается к localhost:5433, потому что работает на компьютере.

## Автоматический запуск всего стенда

Для проверки или восстановления занятия можно выполнить:

    python3 scripts/run_all.py

Этот сценарий автоматически зарегистрирует соединение и датасеты в Superset.
На основном маршруте второго урока он не используется: подключение и Dataset
создаются вручную, чтобы действия были видны студентам.

## Отдельные технические шаги

| Шаг | Команда | Результат |
|---:|---|---|
| 0 | python3 scripts/00_check_environment.py | Проверка Python и Docker |
| 1 | python3 scripts/01_download_data.py | CSV в data/raw |
| 2 | python3 scripts/02_start_database.py | PostgreSQL на localhost:5433 |
| 3 | python3 scripts/03_load_data.py | Таблицы raw и представление analytics |
| 4 | python3 scripts/04_check_data.py | Полная сверка базы с CSV |
| 5 | python3 scripts/05_start_superset.py | Superset на localhost:8088 |
| 6 | python3 scripts/06_connect_superset.py | Автоматическая регистрация датасетов |
| 7 | python3 scripts/07_status.py | Состояние контейнеров |

Каждый шаг можно запускать повторно. Вывод одновременно показывается в
терминале и сохраняется в папке logs.

## Остановка

    python3 scripts/stop.py

Контейнеры остановятся, но PostgreSQL, пользователь Superset, графики и
дашборды сохранятся в Docker volumes.

## Если Docker недоступен

Если сценарий сообщает, что Docker Engine недоступен, запустите Docker Desktop
и дождитесь статуса Engine running:

    open -a Docker
    docker info

Если macOS не находит приложение Docker, сначала установите Docker Desktop:

    brew install --cask docker
    open -a Docker

