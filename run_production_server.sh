#!/bin/bash

HOST=${1:-"localhost"}

echo "HOST: ${HOST}"

export HOST=$HOST
docker compose -f docker-compose.production.yaml up