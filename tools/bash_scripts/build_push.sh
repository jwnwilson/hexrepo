#! /bin/bash

set -e

# check if IMAGE is set
if [ -z "$IMAGE" ]; then
    echo "IMAGE env var is not set"
    exit 1
fi
# check if DOCKER_TAG is set
if [ -z "$DOCKER_TAG" ]; then
    echo "DOCKER_TAG env var is not set"
    exit 1
fi

# Docker login
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 675468650888.dkr.ecr.eu-west-1.amazonaws.com

docker compose build

region="eu-west-1"
aws_ecr="675468650888.dkr.ecr.eu-west-1.amazonaws.com"
ecr_repo_name="hexrepo-${IMAGE}"
# Use last commit datetime as git tag
latest_image=`docker images -q ${IMAGE}`

# tag and push docker image
echo "Tagging and pushing docker image ${latest_image} to ${aws_ecr}/${ecr_repo_name}:${DOCKER_TAG}"
docker tag "${latest_image}" "${aws_ecr}/${ecr_repo_name}:latest"
docker tag "${latest_image}" "${aws_ecr}/${ecr_repo_name}:${DOCKER_TAG}"
docker push "${aws_ecr}/${ecr_repo_name}:latest"
docker push "${aws_ecr}/${ecr_repo_name}:${DOCKER_TAG}"

