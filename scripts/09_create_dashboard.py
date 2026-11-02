from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(
    compose('exec', '-T', 'superset', 'python', '/app/lab/superset/create_dashboard.py'),
    '09_create_dashboard.log',
)
print('✓ Дашборд собран: http://localhost:8088/superset/dashboard/olist-overview/')

