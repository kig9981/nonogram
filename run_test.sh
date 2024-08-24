#!/bin/bash

test_condition=${1:-local}

pytest tests/unit/test_api_server
pytest tests/unit/test_nonogram_server
pytest tests/integration

./run_performance_test.sh $test_condition