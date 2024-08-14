#!/bin/bash

export $(grep -v '^#' .env | xargs)

mkdir -p ./certbot

docker compose -f docker-compose.ssl-certificate.yaml run