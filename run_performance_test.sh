#!/bin/bash

export $(grep -v '^#' tests/test.env | xargs)
locust -f tests/performance/test_nonogram_server/CreateNewSession.py --headless -u 10 --run-time 60s -H http://localhost:${NONOGRAM_SERVER_PORT} --processes 10