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

DB_HOST=
BASTION_INSTANCE=

echo "Activating bastion port forward for: ${PROJECT}, end: ${ENVIRONMENT}" 

aws ssm start-session \
--target ${BASTION_INSTANCE} \
--document-name AWS-StartPortForwardingSession \
--parameters '{"portNumber":["5432"],"localPortNumber":["5432"], "host":["${DB_HOST}"]}'

