import pytest
from django.test.client import RequestFactory


@pytest.fixture
def mock_request():
    return RequestFactory()