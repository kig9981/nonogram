#!/bin/bash

export $(grep -v '^#' .env | xargs)

mkdir -p ./certbot

docker compose -f docker-compose.ssl-certificate.yaml up --exit-code-from certbot