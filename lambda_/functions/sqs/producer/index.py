import json
import os
from time import time_ns

import boto3

SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
IS_FIFO = os.environ["IS_FIFO"]

sqs_client = boto3.client("sqs")

execution_ids = []


def event_handler(event, context):
    cold_start = len(execution_ids) == 0
    execution_id = context.aws_request_id.lower()
    execution_ids.append(execution_id)

    args = {
        "QueueUrl": SQS_QUEUE_URL,
        "MessageBody": json.dumps(
            {
                "producer_cold_start": cold_start,
                "sent_timestamp_ns": time_ns(),
            }
        ),
    }
    if IS_FIFO == "true":
        args["MessageGroupId"] = execution_id

    sqs_client.send_message(**args)
