#!/bin/bash

docker build -f docker/Dockerfile.PythonEnv -t common_base_python:${1:-latest} .
docker build --build-arg VERSION=${1:-latest} -f docker/Dockerfile.NonogramServer -t nonogram_server:${1:-latest} .
docker build --build-arg VERSION=${1:-latest} -f docker/Dockerfile.ApiServer -t api_server:${1:-latest} .
docker build -f docker/Dockerfile.Frontend -t frontend_server:${1:-latest} .
docker image prune -f