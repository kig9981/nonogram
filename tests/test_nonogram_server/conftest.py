import os
import sys
import json
import django
import pytest


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


@pytest.fixture(scope='function')
def django_db_setup(django_db_setup, django_db_blocker, test_boards):
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
