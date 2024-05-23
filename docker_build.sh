#!/bin/bash

docker build -f docker/Dockerfile.NonogramServer -t nonogram_server:${1:-latest} .
docker build -f docker/Dockerfile.ApiServer -t api_server:${1:-latest} .
docker image prune -f