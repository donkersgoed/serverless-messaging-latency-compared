import json
import os
from time import time_ns

import boto3

STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

sfn_client = boto3.client("stepfunctions")

execution_ids = []


def event_handler(_, context):
    cold_start = len(execution_ids) == 0
    execution_id = context.aws_request_id.lower()
    execution_ids.append(execution_id)

    sfn_client.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps(
            {
                "producer_cold_start": cold_start,
                "sent_timestamp_ns": time_ns(),
            }
        ),
    )
