import pytest
from NonogramServer.views import get_nonogram_board
from NonogramServer.views import set_cell_status
from NonogramServer.views import create_new_session
from NonogramServer.views import create_new_game
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


@pytest.mark.django_db
def test_create_new_session(mock_request: RequestFactory):
    url = '/create_new_session/'
    request = mock_request.post(
        path=url,
        data={"session_id": 0},
        content_type="Application/json",
    )
    response = create_new_session(request)
    assert response.content == b"create_new_session(post)"


@pytest.mark.django_db
def test_create_new_game(mock_request: RequestFactory):
    url = '/create_new_game/'
    request = mock_request.post(
        path=url,
        data={"session_id": 0},
        content_type="Application/json",
    )
    response = create_new_game(request)
    assert response.content == b"create_new_game(post)"
