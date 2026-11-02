import os

from superset.app import create_app
from superset import security_manager

app = create_app()
with app.app_context():
    username = os.environ['SUPERSET_ADMIN_USERNAME']
    user = security_manager.find_user(username=username)
    if user is None:
        security_manager.add_user(
            username=username,
            first_name='HSE',
            last_name='Teacher',
            email=os.environ['SUPERSET_ADMIN_EMAIL'],
            role=security_manager.find_role('Admin'),
            password=os.environ['SUPERSET_ADMIN_PASSWORD'],
        )
        print(f'Создан пользователь Superset: {username}')
    else:
        print(f'Пользователь Superset уже существует: {username}')

