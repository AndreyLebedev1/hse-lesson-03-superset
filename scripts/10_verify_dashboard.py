from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(
    compose('exec', '-T', 'superset', 'python', '/app/lab/superset/verify_dashboard.py'),
    '10_verify_dashboard.log',
)
print('✓ Дашборд опубликован и содержит все четыре графика')

