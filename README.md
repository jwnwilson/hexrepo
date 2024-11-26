# Python / Typescript Monorepo

## Setup - AWS

### Prerequesites

- Terraform installed
- Pyenv installed
- AWS account access key and secret
- AWS account permissions set as detailed later
- Route53 domain purchased and setup


### Setup

Setup the following env vars directly or via `make setup`

AWS_ACCOUNT
AWS_DEFAULT_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY


# To Do

- Setup backend
    - Setup pipeline for monorepo
        - Setup test / lint build image
            - Need to dyanmically set poetry cache key to library poetry lock file for correct caching.
            - Look at https://github.com/nektos/act
            - Setup pyright and ruff
            - Port changes to all libs and projects
        - Setup build / db migrate / deploy
            - listen to changes in backend/libs and backend/projects only  
            - Setup db migration
            - Setup deployment
            - Matrix of projects / libs to parallelise
            - Have check in deployment and pass that run if no files changed to trigger deployment
    - Setup infra for projects
        - Update template and verify destroy / rebuild
    - Add ability to update project from template
        - Use cruft to update projects from template?
    - Setup async tasks
        - Conform to ECS / Fargate
        - Setup task chaining with idempotent re-run
    - Setup auth / cross project auth / authorisation
    - Setup mypy
        - Look at ruff
    - Improve docker container builds
        - Setup base lib image to re-use for projects
    - Add user setup to infra as code
        - During project config setup define monorepo user with admin account
        - login with mono repo user and store credentials to work specifically with monorepo
    - Add another cloud provider - GCP
    - Enforce architecture rules:
        - https://roman.pt/posts/python-architecture-linter/
        - [deply](https://github.com/Vashkatsi/deply)

- Setup Frontend
    - Setup micro fe
    - Add app creation script for micro fe
    - Add component lib

- Setup E2E testing

- Automate setup
- Investigate setting up company services
    - Feature Flagging / A / B testing
    - Switching calculation verisons
    - Analytics
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
