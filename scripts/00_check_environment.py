import platform
import subprocess
import sys

from _common import compose, ensure_env, require_docker, run


if sys.version_info < (3, 10):
    raise SystemExit('Нужен Python 3.10 или новее.')

ensure_env()
require_docker()
print(f'✓ Python {platform.python_version()}')
run(compose('version'), '00_environment.log')
print('✓ Среда готова')

