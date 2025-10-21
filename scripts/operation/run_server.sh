#!/bin/zsh

cd ../../aiproxysrv

# Sicherstellen, dass postgres & redis laufen
docker-compose up postgres redis -d

# Warten bis postgres healthy ist
echo "⏳ Waiting for postgres..."
until docker-compose exec -T postgres pg_isready -U aiuser > /dev/null 2>&1; do
  sleep 1
done

# Migration + App-Services starten
docker-compose up db-migration celery-worker aiproxy-app -d

docker ps
