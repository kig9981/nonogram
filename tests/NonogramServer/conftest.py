import pytest
import os

def pytest_configure():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'src.NonogramServer.NonogramServer.settings'