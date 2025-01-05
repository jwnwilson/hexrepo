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
    - Setup serverless async tasks
        - deploy and validate task logic in aws
        - Make dependency handling fastapi compatible check for fastapi depends class
        - task param pydantic style
    - move values from .zshrc to .hexrepo file
    - Play with AI crawler project 
        - Setup crawl spider for PLP pages
        - Cache all page data to avoid recrawls
        - Store data in graph format and visualise it
        - Categorise PLP pages
        - Fan out and crawl web page PDP page contents
    - Create orchestrator project 
        - 1 task table per hexrepo
        - Setup ECS for long running async orchestrator on fargate
            - Could move to celery here as celery doesn't work well with lambda as need to start worker to manage tasks
            - Could wrap celery in task adapter to give it a better interface
        - Setup workflow orchestration
        - Setup Idempotent re-run
        - Dectorator based workflow setup e.g.:
            https://github.com/aws/chalice/blob/master/chalice/app.py#L719
    - Add ability to disable / destroy projects
    - Setup auth / cross project auth / authorisation
    - Setup command to run local against bastion db
    - Improve docker container builds
        - Reduce image size
            https://github.com/astral-sh/uv/issues/8935
        - Setup base lib image to re-use for projects
    - Enforce architecture rules:
        - https://roman.pt/posts/python-architecture-linter/
        - [deply](https://github.com/Vashkatsi/deply)
    - Combine shared infra + env infra pull add envs to config and pull them down
    - Add smoke test / E2E tests
    - Implement template -> project update:
        - Look at cruft again
        - Re-render template with project settings 
        - Create Diff with changes
        - Add CI job to detect template changes and add a new PR with applied patch to projects
    - Add another cloud provider - GCP
    - Add user setup to infra as code
        - During project config setup define hexrepo user with admin account
        - login with mono repo user and store credentials to work specifically with hexrepo

- Full hexrepo setup with hextech cli command like turbo repo
- Investigate setting up company services
    - Create generic hexrepo setup cli tool to setup projects like turborepo
    - Feature Flagging / A / B testing
    - Good stack tracing / logging
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
