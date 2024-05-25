#!/bin/bash

pytest tests/unit/test_api_server
pytest tests/unit/test_nonogram_server
pytest tests/integration