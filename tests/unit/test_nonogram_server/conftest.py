import os
import sys
import json
import django
import pytest
import uuid
import psycopg2
from psycopg2 import OperationalError
from django.conf import settings


def testdb_healthcheck(
    db,
    user,
    password,
    host,
    port,
) -> bool:
    try:
        conn = psycopg2.connect(
            dbname=db,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except OperationalError:
        return False


@pytest.fixture(scope='session')
def django_db_modify_db_settings(
    docker_ip,
    docker_services,
    django_db_modify_db_settings_parallel_suffix,
):
    host = docker_ip
    port = 5433
    user = "testdb"
    password = 'testdbpassword'
    db = "testdb"
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: testdb_healthcheck(db, user, password, host, port)
    )
    settings.DATABASES['default']["NAME"] = db
    settings.DATABASES['default']["USER"] = user
    settings.DATABASES['default']["PASSWORD"] = password
    settings.DATABASES['default']["HOST"] = host
    settings.DATABASES['default']["PORT"] = f"{port}"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(pytestconfig.rootdir.join(os.path.join("tests", "test_database_docker_compose.yaml")))


def pytest_configure():
    sys.path.insert(0, 'src/NonogramServer/')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'NonogramServer.settings'
    django.setup()


@pytest.fixture(scope="session")
def test_boards():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_board_path = os.path.join(test_data_path, 'test_board.json')
    with open(test_board_path, 'r') as f:
        test_boards = json.load(f)

    return test_boards


@pytest.fixture(scope="session")
def test_sessions():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_session_path = os.path.join(test_data_path, 'test_session.json')
    with open(test_session_path, 'r') as f:
        test_sessions = json.load(f)

    return test_sessions


@pytest.fixture(scope="session")
def test_histories():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_history_path = os.path.join(test_data_path, 'test_history.json')
    with open(test_history_path, 'r') as f:
        test_histories = json.load(f)

    return test_histories


@pytest.fixture
def add_board_test_data(
    django_db_setup,
    django_db_blocker,
    test_boards,
):
    from NonogramServer.models import NonogramBoard

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
def add_session_test_data(
    django_db_setup,
    django_db_blocker,
    test_sessions,
):
    from NonogramServer.models import NonogramBoard
    from NonogramServer.models import Session
    from Nonogram.NonogramBoard import NonogramGameplay
    from Nonogram.RealGameBoard import RealGameBoard
    from Nonogram.utils import deserialize_gameboard
    from Nonogram.utils import serialize_gameplay

    for test_session in test_sessions:
        board_id = test_session['board_id']
        with django_db_blocker.unblock():
            board_data = NonogramBoard.objects.get(board_id=board_id)
        real_board = RealGameBoard(
            board_id=board_id,
            board=deserialize_gameboard(board_data.board),
        )
        gameplay = NonogramGameplay(
            board_id=board_id,
            board=real_board,
        ).get_int_board()
        board = serialize_gameplay(gameplay)
        session = Session(
            session_id=test_session['session_id'],
            board_data=board_data,
            board=board,
        )
        with django_db_blocker.unblock():
            session.save()


@pytest.fixture
def add_new_session_test_data(
    django_db_setup,
    django_db_blocker,
    test_sessions,
):
    from NonogramServer.models import Session

    for test_session in test_sessions:
        session = Session(
            session_id=test_session['session_id'],
            board_data=None,
            board=None,
        )
        with django_db_blocker.unblock():
            session.save()


@pytest.fixture
def add_history_test_data(
    django_db_setup,
    django_db_blocker,
    test_histories,
):
    from NonogramServer.models import Session
    from NonogramServer.models import History
    from Nonogram.NonogramBoard import NonogramGameplay
    from Nonogram.utils import serialize_gameplay

    for test_history in test_histories:
        with django_db_blocker.unblock():
            session_data = Session.objects.get(pk=test_history["session_id"])
            board = NonogramGameplay(board_id=session_data.board_data.board_id)
        gameplay_id = uuid.uuid4()
        for current_turn, move in enumerate(test_history["moves"]):
            x = move["x"]
            y = move["y"]
            new_state = move["state"]

            history = History(
                current_session=session_data,
                gameplay_id=gameplay_id,
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


@pytest.fixture
def add_test_data(
    django_db_setup,
    django_db_blocker,
    add_board_test_data,
    add_session_test_data,
    add_history_test_data
):
    pass
