from _common import compose, ensure_env, require_docker, run


ensure_env()
require_docker()
run(
    compose('--profile', 'tools', 'run', '--rm', 'pipeline',
            'python', '/app/pipeline/check.py'),
    '04_check_data.log',
)
print('✓ База полностью совпадает с исходными CSV')

