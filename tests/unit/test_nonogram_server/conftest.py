import os
import sys
import json
import django
import pytest
import psycopg2
from psycopg2 import OperationalError


DB_NAME = "testdb"
DB_USER = "testdb"
DB_PASSWORD = "testdbpassword"
DB_HOST = "localhost"
DB_PORT = 5433


def testdb_healthcheck() -> bool:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
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
    docker_services,
    django_db_modify_db_settings_parallel_suffix,
):
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: testdb_healthcheck()
    )


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(pytestconfig.rootdir.join(os.path.join("tests", "unit", "test_nonogram_server", "test_database_docker_compose.yaml")))


def pytest_configure():
    sys.path.insert(0, 'src/NonogramServer/')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'NonogramServer.settings'
    os.environ["NONOGRAM_SERVER_SECRET_KEY"] = "NONOGRAM_SERVER_SECRET_KEY"
    os.environ["DB_NAME"] = DB_NAME
    os.environ["DB_USER"] = DB_USER
    os.environ["DB_PASSWORD"] = DB_PASSWORD
    os.environ["DB_HOST"] = DB_HOST
    os.environ["DB_PORT"] = f"{DB_PORT}"
    os.environ["NONOGRAM_SERVER_HOST"] = "localhost"
    os.environ["API_SERVER_HOST"] = "localhost"
    os.environ["ENABLE_PROMETHEUS"] = "False"
    os.environ["DEBUG"] = "True"
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
def test_games():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_game_path = os.path.join(test_data_path, 'test_game.json')
    with open(test_game_path, 'r') as f:
        test_games = json.load(f)

    return test_games


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
            black_counter=test_board['black_counter'],
        )
        with django_db_blocker.unblock():
            nonogram_board.save()


@pytest.fixture
def add_game_test_data(
    django_db_setup,
    django_db_blocker,
    add_board_test_data,
    add_session_test_data,
    test_games,
):
    from NonogramServer.models import NonogramBoard
    from NonogramServer.models import Session
    from NonogramServer.models import Game
    from Nonogram.NonogramBoard import NonogramGameplay

    for test_game in test_games:
        board_id = test_game['board_id']
        gameplay_id = test_game['gameplay_id']
        session_id = test_game['session_id']
        
        with django_db_blocker.unblock():
            board_data = NonogramBoard.objects.get(board_id=board_id)
            session = Session.objects.get(session_id=session_id)
            gameplay = NonogramGameplay(
                data=board_data,
                session=session,
                delayed_save=True,
            )
            gameplay.game.gameplay_id = gameplay_id

            gameplay.save()


@pytest.fixture
def add_session_test_data(
    django_db_setup,
    django_db_blocker,
    test_sessions,
):
    from NonogramServer.models import Session

    for test_session in test_sessions:
        session = Session(**test_session)
        with django_db_blocker.unblock():
            session.save()


@pytest.fixture
def add_history_test_data(
    django_db_setup,
    django_db_blocker,
    add_game_test_data,
    test_histories,
):
    from NonogramServer.models import Game
    from Nonogram.NonogramBoard import NonogramGameplay

    for test_history in test_histories:
        with django_db_blocker.unblock():
            gameplay_data = Game.objects.get(gameplay_id=test_history["gameplay_id"])
            board = NonogramGameplay(gameplay_data)
        for move in test_history["moves"]:
            x = move["x"]
            y = move["y"]
            new_state = move["state"]
            with django_db_blocker.unblock():
                board.mark(x, y, new_state)


@pytest.fixture
def add_test_data(
    django_db_setup,
    django_db_blocker,
    add_board_test_data,
    add_game_test_data,
    add_session_test_data,
    add_history_test_data
):
    pass
