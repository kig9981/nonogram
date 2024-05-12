import os
import sys
import django


def pytest_configure():
    sys.path.insert(0, 'src/ApiServer/')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ApiServer.settings'
    os.environ["NONOGRAM_SERVER_PROTOCOL"] = "http"
    os.environ["NONOGRAM_SERVER_HOST"] = "nonogramserver"
    os.environ["NONOGRAM_SERVER_PORT"] = "8000"
    os.environ["API_SERVER_SECRET_KEY"] = "API_SERVER_SECRET_KEY"
    os.environ["DEBUG"] = "True"
    django.setup()
