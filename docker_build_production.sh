#!/bin/bash

docker build -f docker/production/Dockerfile.NonogramServer -t nonogram_server:${1:-latest} .
docker build -f docker/production/Dockerfile.ApiServer -t api_server:${1:-latest} .
docker build -f docker/production/Dockerfile.Frontend -t frontend_server:${1:-latest} .
docker image prune -f