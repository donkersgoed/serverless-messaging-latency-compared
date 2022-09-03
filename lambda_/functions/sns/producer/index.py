import json
import os
from time import time_ns

import boto3

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

sns_client = boto3.client("sns")

execution_ids = []


def event_handler(event, context):
    cold_start = len(execution_ids) == 0
    execution_ids.append(context.aws_request_id.lower())

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(
            {
                "producer_cold_start": cold_start,
                "sent_timestamp_ns": time_ns(),
            }
        ),
    )
