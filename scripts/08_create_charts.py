from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(
    compose('exec', '-T', 'superset', 'python', '/app/lab/superset/create_charts.py'),
    '08_create_charts.log',
)
print('✓ Четыре графика созданы в Superset')

