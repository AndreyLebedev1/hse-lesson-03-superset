import os
from urllib.parse import quote_plus

SECRET_KEY = os.environ['SUPERSET_SECRET_KEY']
SQLALCHEMY_DATABASE_URI = (
    'postgresql+psycopg2://'
    + quote_plus(os.environ['POSTGRES_USER'])
    + ':'
    + quote_plus(os.environ['POSTGRES_PASSWORD'])
    + '@db:5432/superset_meta'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
TALISMAN_ENABLED = False
CONTENT_SECURITY_POLICY_WARNING = False
SESSION_COOKIE_SECURE = False
WTF_CSRF_TIME_LIMIT = None
CACHE_CONFIG = {'CACHE_TYPE': 'SimpleCache'}
DATA_CACHE_CONFIG = {'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 60}
FEATURE_FLAGS = {'DASHBOARD_CROSS_FILTERS': True}
APP_NAME = 'HSE — занятие 3'
ROW_LIMIT = 10000
SQL_MAX_ROW = 10000
LOG_LEVEL = 'WARNING'
