import json
import os
from time import time_ns

import boto3

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
IS_FIFO = os.environ["IS_FIFO"]

sns_client = boto3.client("sns")

execution_ids = []


def event_handler(event, context):
    cold_start = len(execution_ids) == 0
    execution_id = context.aws_request_id.lower()
    execution_ids.append(execution_id)

    args = {
        "TopicArn": SNS_TOPIC_ARN,
        "Message": json.dumps(
            {
                "producer_cold_start": cold_start,
                "sent_timestamp_ns": time_ns(),
            }
        ),
    }

    if IS_FIFO == "true":
        args["MessageGroupId"] = execution_id

    sns_client.publish(**args)
