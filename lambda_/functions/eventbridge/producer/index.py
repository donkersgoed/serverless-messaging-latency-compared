import json
import os
from time import time_ns

import boto3

EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]

eb_client = boto3.client("events")

execution_ids = []


def event_handler(_, context):
    cold_start = len(execution_ids) == 0
    execution_id = context.aws_request_id.lower()
    execution_ids.append(execution_id)

    eb_client.put_events(
        Entries=[
            {
                "EventBusName": EVENT_BUS_NAME,
                "Source": "EventBridgeProducer",
                "DetailType": "ProducerEvent",
                "Detail": json.dumps(
                    {
                        "producer_cold_start": cold_start,
                        "sent_timestamp_ns": time_ns(),
                    }
                ),
            }
        ]
    )
