from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(
    compose('exec', '-T', 'superset', 'python', '/app/lab/superset/register.py'),
    '06_connect_superset.log',
)
print('✓ PostgreSQL подключён к Superset, датасеты зарегистрированы')
print('Откройте http://localhost:8088 и войдите как admin / admin')

