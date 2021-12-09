#!/bin/bash

docker stop database
docker rm database

docker stop frontend
docker rm frontend

docker network rm mynet