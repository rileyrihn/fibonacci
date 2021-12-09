#!/bin/bash

docker network create mynet
docker run -i --name database -p 5432:5432 -e POSTGRES_PASSWORD=testing --network=mynet -d postgres
docker run --name frontend -p 5000:5000 --restart=always --network=mynet -d rileyrihn/fibonacci:latest