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
    - Add project config template
        - prompt for environments
    - Setup infra for projects
        - Setup shared infra build first then environment
    - Setup pipeline
    - Add db adpator logic  
        - Add extra dependencies like boto gcp libs etc
        - Add aws, gcp, azure options to library installs
    - Add ability to update project from template
        - Use cruft to update projects from template?    
    - Add storage libs for gcp, aws, azure
    - Setup async tasks
        - Setup task chaining with idempotent re-run
    - Setup auth / cross project auth / client
    - Setup mypy
        - Look at ruff
    - Setup docker container builds
        - Setup base lib image to re-use for projects
    - Add user setup to infra as code
        - During project config setup define monorepo user with admin account
        - login with mono repo user and store credentials to work specifically with monorepo


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
    - Free infra under my own domain to allow users to try it out

Tools to looks at
- stackshare to see what services / tools companies use
    https://stackshare.io/uber-technologies/uber
