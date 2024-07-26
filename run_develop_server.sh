#!/bin/bash

HOST=${1:-"localhost"}

echo "HOST: ${HOST}"

HOST=$HOST docker compose -f docker-compose.develop.yaml up