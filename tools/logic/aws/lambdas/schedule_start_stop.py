import boto3
import os

region = os.environ['region']


def lambda_handler(event, context):
    # Start or stop EC2 based on start / stop tags
    start_stop_ec2(region)
    start_stop_rds(region)
            