import os
import sys
import django


def pytest_configure():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'NonogramServer.settings'
    sys.path.insert(0, 'src/NonogramServer/')
    django.setup()
