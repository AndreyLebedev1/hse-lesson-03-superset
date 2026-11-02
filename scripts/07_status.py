from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(compose('ps'), '07_status.log')
print('DBeaver:  localhost:5433 / olist / olist_admin / olist_local')
print('Superset: http://localhost:8088 / admin / admin')

