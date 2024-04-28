import pytest
import json
import os
from NonogramServer.models import NonogramBoard
from Nonogram.utils import serialize_gameboard
from NonogramServer.views import get_nonogram_board
from NonogramServer.views import set_cell_status
from NonogramServer.views import create_new_session
from NonogramServer.views import create_new_game
from django.test.client import RequestFactory


def get_test_board():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_board_path = os.path.join(test_data_path, 'test_board.json')
    with open(test_board_path, 'r') as f:
        test_boards = json.load(f)

    return test_boards


@pytest.fixture(scope='function')
def django_db_setup(django_db_setup, django_db_blocker):
    test_boards = get_test_board()
    for test_board in test_boards:
        nonogram_board = NonogramBoard(
            board_id=test_board['board_id'],
            board=test_board['board'],
            num_row=test_board['num_row'],
            num_column=test_board['num_column'],
            theme="test data",
        )
        with django_db_blocker.unblock():
            nonogram_board.save()


@pytest.fixture
def mock_request():
    return RequestFactory()


@pytest.mark.django_db
def test_get_nonogram_board(mock_request: RequestFactory):
    url = '/get_nonogram_board/'

    test_boards = get_test_board()

    for test_board in test_boards:
        query_dict = {
            "session_id": 0,
            "board_id": test_board['board_id'],
        }
        query = json.dumps(query_dict)
        request = mock_request.post(
            path=url,
            data=query,
            content_type="Application/json",
        )
        response = get_nonogram_board(request)

        assert response.status_code == 200

        response_data = json.loads(response.content)

        assert response_data["board"] == test_board["board"]
        assert response_data["num_row"] == test_board["num_row"]
        assert response_data["num_column"] == test_board["num_column"]



@pytest.mark.django_db
def test_set_cell_status(mock_request: RequestFactory):
    url = '/set_cell_status/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = set_cell_status(request)
    assert response.content == b"set_cell_status(post)"


@pytest.mark.django_db
def test_create_new_session(mock_request: RequestFactory):
    url = '/create_new_session/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = create_new_session(request)
    assert response.content == b"create_new_session(post)"


@pytest.mark.django_db
def test_create_new_game(mock_request: RequestFactory):
    url = '/create_new_game/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = create_new_game(request)
    assert response.content == b"create_new_game(post)"
