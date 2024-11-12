# Python / Typescript Monorepo

## Setup - AWS

### Prerequesites

- Terraform installed
- Pyenv installed
- AWS account access key and secret
- AWS account permissions to create / modify:
    - KMS
    - code artifact
    - ECS
    - ECR
    - VPC
    - API gateway

### Setup

Setup the following env vars directly or via `make setup`

AWS_ACCOUNT
AWS_DEFAULT_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY


# To Do

- Setup backend
    - Setup lib install from deployed libraries
    - Setup infra for projects
    - Add db adpator logic  
        - Add aws, gcp, azure options to library installs
    - Setup easy lib development with prod groups
        - https://github.com/python-poetry/poetry/issues/9611
    - Add ability to update project from template
        - Use cruft to update projects from template?    
    - Add storage libs for gcp, aws, azure
    - Setup async tasks
    - Setup auth / cross project auth / client
    - Setup pipeline
    - Setup mypy

- Setup Frontend
    - Setup micro fe
    - Add app creation script for micro fe
    - Add component lib

- Setup E2E testing

- Automate setup
- Investigate setting up company services
    - JIRA / Confluence
    - Spendesk
    - Charlie hr
    - Product board
    - Payments
    - Automated API docs
    - External APIs
    - Serverless setup
