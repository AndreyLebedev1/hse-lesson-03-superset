from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(compose('up', '-d', '--wait', 'superset'), '05_start_superset.log')
print('✓ Superset открыт на http://localhost:8088')

