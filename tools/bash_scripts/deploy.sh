#! /bin/bash

set -e

region="eu-west-1"
aws_ecr="675468650888.dkr.ecr.eu-west-1.amazonaws.com"
ecr_repo_name="monorepo-example"
latest_image=`docker images -q example`
# Use last commit datetime as git tag
docker_tag=$(git log -n1 --pretty='format:%cd' --date=format:'%Y%m%d%H%M%S')

# Docker login
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 675468650888.dkr.ecr.eu-west-1.amazonaws.com

docker compose build

# tag and push docker image
docker tag "${latest_image}" "${aws_ecr}/${ecr_repo_name}:latest"
docker tag "${latest_image}" "${aws_ecr}/${ecr_repo_name}:${docker_tag}"
docker push "${aws_ecr}/${ecr_repo_name}:latest"
docker push "${aws_ecr}/${ecr_repo_name}:${docker_tag}"

if [[ ${NO_INPUT} == "true" ]] then;
    make tf_apply_no_input TF_VAR_docker_tag=${docker_tag}
else
    make tf_apply TF_VAR_docker_tag=${docker_tag}
fi
