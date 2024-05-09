import os
import sys
import django


def pytest_configure():
    sys.path.insert(0, 'src/ApiServer/')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ApiServer.settings'
    django.setup()
