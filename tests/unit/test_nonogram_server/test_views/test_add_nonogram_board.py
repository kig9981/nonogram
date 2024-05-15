import pytest
import os
import io
import base64
from http import HTTPStatus
from NonogramServer.views.AddNonogramBoard import AddNonogramBoard
from django.test.client import RequestFactory
from PIL import Image
from ...util import send_test_request

add_nonogram_board = AddNonogramBoard.as_view()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_add_nonogram_board(
    mock_request: RequestFactory,
):
    url = '/add_nonogram_board/'
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_image_path = os.path.join(test_data_path, 'test_board_image.jpg')
    with Image.open(test_image_path) as img:
        num_row, num_column = img.size
        byte_image = io.BytesIO()
        img.save(byte_image, format="JPEG")
        b64_image = base64.b64encode(byte_image.getvalue()).decode()

    query_dict = {
        'board': b64_image,
        'num_row': num_row,
        'num_column': num_column,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=add_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.OK

    b64_text = base64.b64encode(b"test image string").decode()

    query_dict = {
        'board': b64_text,
        'num_row': num_row,
        'num_column': num_column,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=add_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
