import pytest
from src.NonogramServer.NonogramServer.views import get_nonogram_board
from django.test.client import RequestFactory

@pytest.fixture
def mock_request():
    return RequestFactory()

def test_get_nonogram_board(mock_request: RequestFactory):
    url = '/get_nonogram_board/'
    request = mock_request.post(
        path=url,
        data={"board_id": 0},
        content_type="Application/json",
    )
    response = get_nonogram_board(request)
    assert response.content == b"get_nonogram_board"