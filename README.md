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
    - Create run_be with django ninja
        - Setup Auth and permissiong / feature flags 
        - Update template add django ninja option
    - Setup simple FE with auth?
        - Add auth
            - Auth0
        - User Event tracking
            - Mixpanel
    - Cheaper infra / kubernetes?
        - Scaleway cheap kubernetes cluster?
        - GCP?
        - Use 3rd party auth provider to avoid vender locking?
    - Create orchestrator logic
        - Setup Flower 
        - Setup airflow / prefect on ECS / EC2 / K8s
            - Look at prefect as less effort to implement?
        - Setup task tracking debugging UI
            - Airflow?
                - This will likely require EC2 / kubernetes due to number of containers
                - https://github.com/jwnwilson/airflow-kubernetes/tree/main
    - Add monitoring dashboard for services
        - Look at graphana
        - Look at logfire
        - Generic change log syncing to tracking metrics
        - Add log based event tracking
        - Change data capture streaming to data warehouse
        - Potentially use 3rd party service?
        - Load testing
        - Latency tracking and visualisation
        - Setup BI dashboard
        - Setup sonarqube
    - Convert fastapi to async for thoughput in APIs
    - Update templates
        - Add FE template hextool option
    - branch deploys
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
    - Add ability to disable / turn off / turn on projects
    - Add smoke test / E2E tests
    - Add user setup to infra as code
        - During project config setup define hexrepo user with admin account
        - login with mono repo user and store credentials to work specifically with hexrepo

### Project Ideas
    - Cycling running area capture app.
        - Map strava data to a map to show the total area you have covered
        - AI agents to proactively onboard new users
    - Bunny App
    - Start up starter kit
        - UI to manage the app and link to all services
            - Company index
        - Feature Flagging / A / B testing
        - Better stack tracing / logging
        - Analytics - Graphana?
        - JIRA / Confluence
        - Spendesk
        - Charlie hr
        - Product board
        - Payments
        - Automated API docs
        - External APIs
        - Free infra under my own domain to allow users to try it out
    - Play with AI crawler project 
        - Setup crawl spider for PLP pages
        - Cache all page data to avoid recrawls
        - Store data in graph format and visualise it
        - Categorise PLP pages
        - Fan out and crawl web page PDP page contents

- Setup Frontend
    - rename project -> backend?
    - create frontend folder?
    - Setup micro fe
    - Add app creation script for micro fe
    - Add component lib

Tools to looks at
- stackshare to see what services / tools companies use
    https://stackshare.io/uber-technologies/uber
