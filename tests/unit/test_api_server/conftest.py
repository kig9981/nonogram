import os
import sys
import django


def pytest_configure():
    sys.path.insert(0, 'src/ApiServer/')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ApiServer.settings'
    os.environ["API_SERVER_SECRET_KEY"] = "API_SERVER_SECRET_KEY"
    django.setup()
