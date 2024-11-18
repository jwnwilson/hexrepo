!# /bin/bash

aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 675468650888.dkr.ecr.eu-west-1.amazonaws.com

docker compose build

docker tag monorepo:latest 675468650888.dkr.ecr.eu-west-1.amazonaws.com/monorepo-example:latest

docker push 675468650888.dkr.ecr.eu-west-1.amazonaws.com/monorepo-example:latest
