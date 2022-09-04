import json
import os
from time import time_ns

import boto3

KDS_STREAM_NAME = os.environ["KDS_STREAM_NAME"]

kinesis_client = boto3.client("kinesis")

execution_ids = []


def event_handler(_, context):
    cold_start = len(execution_ids) == 0
    execution_id = context.aws_request_id.lower()
    execution_ids.append(execution_id)

    kinesis_client.put_record(
        StreamName=KDS_STREAM_NAME,
        Data=json.dumps(
            {
                "producer_cold_start": cold_start,
                "sent_timestamp_ns": time_ns(),
            }
        ),
        PartitionKey=execution_id,
    )
