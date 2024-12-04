# Python Monorepo

This is my python monorepo that uses hexagonal architecture to manage complexity. 

Features include:

- CLI commands to setup projects
- CLI to create libraries and add them to project
- Auto update projects when a library is updated
- Auto update projects infra as code when shared infra as code if modified
- Local debugging of library code while developing
- Automatic deployment of libraries and projects 

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
        - Setup build / db migrate / deploy
            - Setup db migration
            - Setup deployment
            - Auto increment version in pipeline
                - Add githook to check if version needs to be increased
                - Add command to bump library version
        - Move lib & project tools to root tools folder to remove duplication
    - Add ability to update project from template
        - Use cruft to update projects from template?
        - Update template and verify destroy / rebuild
        - Add project & library setup test
    - Setup async tasks
        - Conform to ECS / Fargate
        - Setup task chaining with idempotent re-run
    - Setup auth / cross project auth / authorisation
    - Improve docker container builds
        - Setup base lib image to re-use for projects
    - Add user setup to infra as code
        - During project config setup define monorepo user with admin account
        - login with mono repo user and store credentials to work specifically with monorepo
    - Add another cloud provider - GCP
    - Enforce architecture rules:
        - https://roman.pt/posts/python-architecture-linter/
        - [deply](https://github.com/Vashkatsi/deply)
    - Setup test / lint build image
            - Look at https://github.com/nektos/act
            - Setup pyright and ruff
            - Port changes to all libs and projects

- Setup Frontend
    - Move to seperate repo
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
