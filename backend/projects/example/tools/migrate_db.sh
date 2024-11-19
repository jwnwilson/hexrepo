#! /bin/bash

set -e
set -x

source $(dirname "$0")/util.sh

# Trigger db migrate lambda function
cd infra/tf/aws/environment

# Get name of lambda to run
LAMBDA_NAME=`terraform output -raw db_migrator_lambda_name`

# Trigger lambda
RESULT=`aws lambda invoke --function-name $LAMBDA_NAME --payload '{}' response.json`

# Wait for result of lambda
jq '.' response.json

ERROR=`jq '.FunctionError' <<< $RESULT`

if [ "$ERROR" != "null" ]; then
    echo "Error calling migrate DB command"
    exit 1
else
    echo "DB migration successful."
fi