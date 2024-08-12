#!/bin/bash

HOST=${1:-"localhost"}

echo "HOST: ${HOST}"

envsubst < ./prometheus/prometheus.yaml.template > ./prometheus/.temp/prometheus.yaml

export HOST=$HOST
docker compose -f docker-compose.develop.yaml up

rm ./prometheus/.temp/prometheus.yaml