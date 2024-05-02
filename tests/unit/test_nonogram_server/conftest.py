import os
import sys
import json
import django
import pytest
import uuid


def pytest_configure():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'NonogramServer.settings'
    sys.path.insert(0, 'src/NonogramServer/')
    django.setup()


@pytest.fixture
def test_boards():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_board_path = os.path.join(test_data_path, 'test_board.json')
    with open(test_board_path, 'r') as f:
        test_boards = json.load(f)

    return test_boards


@pytest.fixture
def test_sessions():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_session_path = os.path.join(test_data_path, 'test_session.json')
    with open(test_session_path, 'r') as f:
        test_sessions = json.load(f)

    return test_sessions


@pytest.fixture
def test_histories():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_history_path = os.path.join(test_data_path, 'test_history.json')
    with open(test_history_path, 'r') as f:
        test_histories = json.load(f)

    return test_histories


@pytest.fixture
def add_test_data(
    django_db_setup,
    django_db_blocker,
    test_boards,
    test_sessions,
    test_histories,
):
    from NonogramServer.models import NonogramBoard
    from NonogramServer.models import Session
    from NonogramServer.models import History
    from Nonogram.NonogramBoard import NonogramGameplay
    from Nonogram.utils import serialize_gameplay

    for test_board in test_boards:
        nonogram_board = NonogramBoard(
            board_id=uuid.UUID(test_board['board_id']),
            board=test_board['board'],
            num_row=test_board['num_row'],
            num_column=test_board['num_column'],
            theme="test data",
        )
        with django_db_blocker.unblock():
            nonogram_board.save()

    for test_session in test_sessions:
        with django_db_blocker.unblock():
            board_data = NonogramGameplay(
                board_id=uuid.UUID(test_session['board_id']),
            ).get_int_board()
        board = serialize_gameplay(board_data)
        session = Session(
            session_id=uuid.UUID(test_session['session_id']),
            board_data_id=uuid.UUID(test_session['board_id']),
            board=board,
        )
        with django_db_blocker.unblock():
            session.save()

    for gameplay_id, test_history in enumerate(test_histories):
        with django_db_blocker.unblock():
            session_data = Session.objects.get(pk=uuid.UUID(test_history["session_id"]))
            board = NonogramGameplay(board_id=session_data.board_data.board_id)
        for current_turn, move in enumerate(test_history["moves"]):
            x = move["x"]
            y = move["y"]
            new_state = move["state"]

            history = History(
                current_session=session_data,
                gameplay_id=gameplay_id + 1,
                current_turn=current_turn + 1,
                type_of_move=new_state,
                x_coord=x,
                y_coord=y,
            )
            board.mark(x, y, new_state)
            with django_db_blocker.unblock():
                history.save()
                session_data.current_game = history
                session_data.board = serialize_gameplay(board.get_int_board())
                session_data.save()
