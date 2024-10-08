#!/bin/bash

test_condition=${1:-local}

echo "test condition = $test_condition"

if [[ $test_condition == "local" ]]; then
    export $(grep -v '^#' tests/test.env | xargs)
    export TEST_CONDITION="local"
    locust -f tests/performance/CreateNewSession.py --headless -u 100 --run-time 60s -H http://localhost:${API_SERVER_PORT} --processes 5
    locust -f tests/performance/CreateNewGame.py --headless -u 100 --run-time 60s -H http://localhost:${API_SERVER_PORT} --processes 5
    locust -f tests/performance/GamePlay.py --headless -u 100 --run-time 60s -H http://localhost:${API_SERVER_PORT} --processes 5
elif [[ $test_condition == "production" ]]; then
    export $(grep -v '^#' .env | xargs)
    export TEST_CONDITION="production"
    locust -f tests/performance/CreateNewSession.py --headless -u 100 --run-time 60s -H ${SERVER_PROTOCOL}://${SERVER_DOMAIN}/api --processes 5
    locust -f tests/performance/CreateNewGame.py --headless -u 100 --run-time 60s -H ${SERVER_PROTOCOL}://${SERVER_DOMAIN}/api --processes 5
    locust -f tests/performance/GamePlay.py --headless -u 100 --run-time 60s -H ${SERVER_PROTOCOL}://${SERVER_DOMAIN}/api --processes 5
else
    echo "Invalid test condition"
fi