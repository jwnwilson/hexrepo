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
    - Add ECS option (make default) to avoid cold startup and avoid aws lockin
        - Simplify to ALB -> ECS
            - create new infra setup module
        - Docker tag not being passed to the tf apply
            - Move to hextech
        - Keep lambda gateway option / run both in parallel for the lols and compare
    - Create orchestrator logic
        - Standard async tasks with celery + SQS + container
            - Keep serverless tasks as option
        - Setup airflow / prefect on ECS / EC2
        - Setup task tracking debugging UI
            - Flower? 
            - Airflow?
    - Add monitoring dashboard for services
        - Look at graphana?
        - Generic change log syncing to tracking metrics
        - Add log based event tracking
        - Change data capture streaming to data warehouse
        - Potentially use 3rd party service?
        - Load testing
        - Latency tracking and visualisation
        - Setup BI dashboard
        - Setup sonarqube
    - monolith / multiteam setup
        - team folders
        - Remove lib type
        - tach: https://github.com/gauge-sh/tach
        - https://roman.pt/posts/python-architecture-linter/
        - restricting adaptors imports to a dependencies module
    - blue green deployments via load balancer
    - Setup multienv
        - Enable disable project via admin
        - Create staging and prod envs
        - Simplify feature flags to be for one env
        - feature flag env -> company flag env
    - Improve pipeline yaml, update cli commands to update yaml to add and remove projects
    - Copier
        - Support no db and uncomment test
        - Support nosql db and uncomment test
    - Add API lib to call projects and pass request-id-header
    - versions endpoint if versions enabled
        https://sqlalchemy-continuum.readthedocs.io/en/latest/
    - Improve feature flags
        - Add setup data command to add envs with config
        - Optimise feature flag endpoint with a db view caching or something
    - Setup simple FE with auth?
        - Create apps folder for FE
        - User Event tracking
        - Add turborepo with auth
    - Play with AI crawler project 
        - Setup crawl spider for PLP pages
        - Cache all page data to avoid recrawls
        - Store data in graph format and visualise it
        - Categorise PLP pages
        - Fan out and crawl web page PDP page contents
    - Add ability to disable / turn off / turn onn projects
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
