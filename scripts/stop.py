from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(compose('down'), 'stop.log')
print('Контейнеры остановлены. Данные PostgreSQL и Superset сохранены.')

