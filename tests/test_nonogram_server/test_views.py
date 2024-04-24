import pytest
from NonogramServer.views import get_nonogram_board
from NonogramServer.views import set_cell_status
from django.test.client import RequestFactory


@pytest.fixture
def mock_request():
    return RequestFactory()


@pytest.mark.django_db
def test_get_nonogram_board(mock_request: RequestFactory):
    url = '/get_nonogram_board/'
    request = mock_request.post(
        path=url,
        data={"session_id": 0},
        content_type="Application/json",
    )
    response = get_nonogram_board(request)
    assert response.content == b"get_nonogram_board(post)"

@pytest.mark.django_db
def test_set_cell_status(mock_request: RequestFactory):
    url = '/set_cell_status/'
    request = mock_request.post(
        path=url,
        data={"session_id": 0},
        content_type="Application/json",
    )
    response = set_cell_status(request)
    assert response.content == b"set_cell_status(post)"