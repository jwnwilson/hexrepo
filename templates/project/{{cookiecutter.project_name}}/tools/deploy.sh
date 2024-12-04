#! /bin/bash

aws ecr get-login-password --region {{cookiecutter.cloud_provider_auth_region}} | docker login --username AWS --password-stdin {{cookiecutter.cloud_provider_auth_account_id}}.dkr.ecr.{{cookiecutter.cloud_provider_auth_region}}.amazonaws.com

docker compose build

docker tag {{cookiecutter.project_slug}}:latest {{cookiecutter.cloud_provider_auth_account_id}}.dkr.ecr.{{cookiecutter.cloud_provider_auth_region}}.amazonaws.com/monorepo-{{cookiecutter.project_slug}}:latest

docker push {{cookiecutter.cloud_provider_auth_account_id}}.dkr.ecr.{{cookiecutter.cloud_provider_auth_region}}.amazonaws.com/monorepo-{{cookiecutter.project_slug}}:latest
