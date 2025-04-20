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
- python uv intalled
- An AWS Account with:
    - AWS account access key and secret
    - AWS account permissions set as detailed later
- AWS CLI + SSM installed:
    https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html#install-plugin-macos
- Route53 domain purchased if API setup required


### Setup

Setup the following env vars directly or run:

`make setup`

# To Do

- Setup backend
    - Update feature flags so they are shared across companies by default and can be overriden on a per company bases
        - Fix delete feature flag bug
        - Add company and user overrides to feature flags
        - Add setup data command to add envs with config
    - Authentication via fastapi middleware infra agnostic solution
        - Get user data with permissions via api call with username from header or session.
        - Improve DB calls to make more performant
        - Create materialised view or cache in dynamodb for cheap serverless option?
    - Disable example project
    - Add ECS option to avoid cold startup and avoid aws lockin
        - blue green deployments
        - prod image that is fast to deploy on all envs
    - Implement template -> project update:
        - Copier https://copier.readthedocs.io/en/stable/
        - Look at cruft again
        - Re-render template with project settings 
        - Create Diff with changes
        - Add CI job to detect template changes and add a new PR with applied patch to projects
        - Enable disable project via admin
    - Setup sonarqube
    - versions endpoint if versions enabled
        https://sqlalchemy-continuum.readthedocs.io/en/latest/
    - Add API lib to call projects and pass request-id-header
    - Add monitoring dashboard for services
        - Generic change log syncing to tracking metrics
        - Add log based event tracking
        - Change data capture streaming to data warehouse
        - Potentially use 3rd party service?
        - Load testing
        - Latency tracking and visualisation
        - Setup BI dashboard
    - Tests:
        - Test auth and permission logic
        - Test cloud libs
        - Test Auth / authorisation
    - Setup simple FE with auth?
        - Rename projects -> backend
        - Create frontend folder
        - Add turborepo with auth
    - Create orchestrator / workflow project 
        - Investigate better fire and forget task setup like run 1 off ECS / GCP job with task status update?
        - 1 task table per hexrepo
        - Setup ECS for long running async orchestrator on fargate
            - Schedule this to turn off when not in use
        - Setup workflow orchestration
        - Setup Idempotent re-run
        - Dectorator based workflow setup e.g.:
            https://github.com/aws/chalice/blob/master/chalice/app.py#L719 
    - Enforce architecture rules:
        - Remove lib type
        - tach: https://github.com/gauge-sh/tach
        - https://roman.pt/posts/python-architecture-linter/
        - restricting adaptors imports to a dependencies module
    - Play with AI crawler project 
        - Setup crawl spider for PLP pages
        - Cache all page data to avoid recrawls
        - Store data in graph format and visualise it
        - Categorise PLP pages
        - Fan out and crawl web page PDP page contents
    - Add ability to disable / destroy projects
    - Improve docker container builds
        - Reduce image size
            https://github.com/astral-sh/uv/issues/8935
        - Setup base lib image to re-use for projects
    - Combine shared infra + env infra pull add envs to config and pull them down
    - Project improvements
        - set pythonpath in vscode settings to current project command
    - Add smoke test / E2E tests
    - Add user setup to infra as code
        - During project config setup define hexrepo user with admin account
        - login with mono repo user and store credentials to work specifically with hexrepo

- Investigate setting up company services
    - Create generic hexrepo setup cli tool to setup projects like turborepo
    - Feature Flagging / A / B testing
    - Switching calculation verisons
    - Better stack tracing / logging
    - Analytics
    - JIRA / Confluence
    - Spendesk
    - Charlie hr
    - Product board
    - Payments
    - Automated API docs
    - External APIs
    - Free infra under my own domain to allow users to try it out

- Setup Frontend
    - rename project -> backend?
    - create frontend folder?
    - Setup micro fe
    - Add app creation script for micro fe
    - Add component lib

Tools to looks at
- stackshare to see what services / tools companies use
    https://stackshare.io/uber-technologies/uber
