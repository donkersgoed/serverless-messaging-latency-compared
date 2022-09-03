import json
import os
from time import time_ns

import boto3

SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]

sqs_client = boto3.client("sqs")

execution_ids = []


def event_handler(event, context):
    cold_start = len(execution_ids) == 0
    execution_ids.append(context.aws_request_id.lower())

    sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(
            {
                "producer_cold_start": cold_start,
                "sent_timestamp_ns": time_ns(),
            }
        ),
    )
