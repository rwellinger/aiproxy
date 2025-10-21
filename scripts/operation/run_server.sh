#!/bin/zsh

cd ../../aiproxysrv

docker-compose up db-migration celery-worker aiproxy-app -d
docker ps
