#!/bin/bash

export $(grep -v '^#' .env | xargs)

mkdir -p ./prometheus/.temp/
rm -f ./prometheus/.temp/prometheus.yaml

envsubst < ./prometheus/prometheus.yaml.template > ./prometheus/.temp/prometheus.yaml

mkdir -p ./grafana

docker compose -f docker-compose.develop.yaml up

rm ./prometheus/.temp/prometheus.yaml