import json
import os
from time import time_ns

import boto3

DDB_TABLE_NAME = os.environ["DDB_TABLE_NAME"]

ddb_client = boto3.client("dynamodb")

execution_ids = []


def event_handler(_, context):
    cold_start = len(execution_ids) == 0
    execution_id = context.aws_request_id.lower()
    execution_ids.append(execution_id)

    ddb_client.put_item(
        TableName=DDB_TABLE_NAME,
        Item={
            "PK": {"S": execution_id},
            "producer_cold_start": {"BOOL": cold_start},
            "sent_timestamp_ns": {"N": str(time_ns())},
        },
    )
