#!/bin/bash

export $(grep -v '^#' .env | xargs)

mkdir -p ./certbot