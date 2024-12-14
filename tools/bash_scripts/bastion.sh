#! /bin/bash
set -e

if [[ -z "$ENVIRONMENT"]] then;
    echo "ENVIRONMENT is not set. Exiting."
    exit 1
fi

if [[ -z "$PROJECT"]] then;
    echo "PROJECT is not set. Exiting."
    exit 1
fi

DB_HOST=$(aws rds describe-db-instances --query 'DBInstances[].DBInstanceStatus[]')
BASTION_INSTANCE=

echo "Activating bastion port forward for: ${PROJECT}, end: ${ENVIRONMENT}" 

aws ssm start-session \
--target i-0ebb96e385446d037 \
--document-name AWS-StartPortForwardingSessionToRemoteHost \
--parameters '{"portNumber":["5432"],"localPortNumber":["5432"], "host":["example-db-default.clfqqiusnlbr.eu-west-1.rds.amazonaws.com"]}'

