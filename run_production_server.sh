#!/bin/bash

HOST=${1:-"localhost"}

echo "HOST: ${HOST}"

export $(grep -v '^#' .env | xargs)

mkdir -p ./prometheus/.temp/
rm -f ./prometheus/.temp/prometheus.yaml

envsubst < ./prometheus/prometheus.yaml.template > ./prometheus/.temp/prometheus.yaml

mkdir -p ./grafana

export HOST=$HOST
docker compose -f docker-compose.production.yaml up