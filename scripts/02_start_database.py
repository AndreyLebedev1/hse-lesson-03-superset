from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(compose('up', '-d', '--wait', 'db'), '02_start_database.log')
print('✓ PostgreSQL работает на localhost:5433')

