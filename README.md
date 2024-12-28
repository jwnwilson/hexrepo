# Hextech Monorepo

This is my python monorepo inspired by tools like turborepo that uses hexagonal architecture to manage complexity to create modular reuseable code. 

![alt text](docs/hextech.png)

Features include:

- CLI commands to setup projects
- CLI to create libraries and add them to project
- Auto update projects when a library is updated
- Auto update infra as code when shared infra as code is modified
- Local debugging of library code while developing
- Automatic deployment of libraries and projects 

## Setup - AWS

### Prerequesites

- Terraform installed
- Pipx & Pyenv installed
- An AWS Account with:
    - AWS account access key and secret
    - AWS account permissions set as detailed later
- Route53 domain purchased if API setup required
- AWS CLI + SSM installed:
    https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html#install-plugin-macos


### Setup

Setup the following env vars directly or run:

`make setup`

```
AWS_ACCOUNT
AWS_DEFAULT_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

# To Do

- Setup backend
    - Improve dynamodb
    - Play with AI crawler project 
        - Add file storage
        - Setup async tasks
            - migrate hex lib into this repo
                https://github.com/jwnwilson/hex-lib/tree/main/src/hex_lib/adapter/out
            - SQS + lambda
            - Setup task chaining with idempotent re-run
        - Setup crawl spider
        - Store data in graph format and visualise it
        - Categorise web pages
    - Add ability to disable / destroy projects
    - Setup auth / cross project auth / authorisation
    - Implement template -> project update:
        - Look at cruft again
        - Re-render template with project settings 
        - Create Diff with changes
        - Add CI job to detect template changes and add a new PR with applied patch to projects
    - Setup command to run local against bastion db
    - Improve docker container builds
        - Reduce image size
            https://github.com/astral-sh/uv/issues/8935
        - Setup base lib image to re-use for projects
    - Add user setup to infra as code
        - During project config setup define monorepo user with admin account
        - login with mono repo user and store credentials to work specifically with monorepo
    - Enforce architecture rules:
        - https://roman.pt/posts/python-architecture-linter/
        - [deply](https://github.com/Vashkatsi/deply)
    - Combine shared infra + env infra pull add envs to config and pull them down
    - Add smoke test / E2E tests
    - Add another cloud provider - GCP

- Full monorepo setup with hextech cli command like turbo repo
- Investigate setting up company services
    - Create generic monorepo setup cli tool to setup projects like turborepo
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

- Setup Frontend
    - Setup micro fe
    - Add app creation script for micro fe
    - Add component lib

Tools to looks at
- stackshare to see what services / tools companies use
    https://stackshare.io/uber-technologies/uber
