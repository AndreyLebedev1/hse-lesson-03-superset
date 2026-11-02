from _common import ROOT, compose, ensure_env, require_docker, run


required = ROOT / 'data' / 'raw' / 'sources.json'
if not required.exists():
    raise SystemExit('Сначала запустите 01_download_data.py')

ensure_env()
require_docker()
run(
    compose('--profile', 'tools', 'run', '--rm', '--build', 'pipeline',
            'python', '/app/pipeline/load.py'),
    '03_load_data.log',
)
print('✓ Данные загружены в PostgreSQL')

