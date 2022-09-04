"""Module for the main ServerlessMessagingLatencyCompared Stack."""

import json
from typing import List, Dict

# Third party imports
from aws_cdk import Stack, aws_cloudwatch as cloudwatch
from constructs import Construct

# Local application/library specific imports
from serverless_messaging_latency_compared.constructs.sqs_test import SqsTest
from serverless_messaging_latency_compared.constructs.sqs_fifo_test import SqsFifoTest
from serverless_messaging_latency_compared.constructs.sns_test import SnsTest
from serverless_messaging_latency_compared.constructs.sns_fifo_test import SnsFifoTest
from serverless_messaging_latency_compared.constructs.kinesis_test import KinesisTest
from serverless_messaging_latency_compared.constructs.kinesis_efo_test import (
    KinesisEfoTest,
)
from serverless_messaging_latency_compared.constructs.sfn_standard_test import (
    SfnStandardTest,
)
from serverless_messaging_latency_compared.constructs.sfn_express_test import (
    SfnExpressTest,
)
from serverless_messaging_latency_compared.constructs.eventbridge_test import (
    EventBridgeTest,
)


PERCENTILES = [10, 50, 90, 99]


class ServerlessMessagingLatencyComparedStack(Stack):
    """The ServerlessMessagingLatencyCompared Stack."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Construct a new ServerlessMessagingLatencyComparedStack."""
        super().__init__(scope, construct_id, **kwargs)

        sqs_test = SqsTest(
            scope=self, construct_id="SqsTest", messaging_type="SQS Standard"
        )
        sqs_fifo_test = SqsFifoTest(
            scope=self, construct_id="SqsFifoTest", messaging_type="SQS FIFO"
        )
        sns_test = SnsTest(
            scope=self, construct_id="SnsTest", messaging_type="SNS Standard"
        )
        sns_fifo_test = SnsFifoTest(
            scope=self, construct_id="SnsFifoTest", messaging_type="SNS FIFO"
        )
        sfn_standard_test = SfnStandardTest(
            scope=self, construct_id="SfnStandardTest", messaging_type="SFN Standard"
        )
        sfn_express_test = SfnExpressTest(
            scope=self, construct_id="SfnExpressTest", messaging_type="SFN Express"
        )
        event_bridge_test = EventBridgeTest(
            scope=self, construct_id="EventBridgeTest", messaging_type="EventBridge"
        )
        kinesis_test = KinesisTest(
            scope=self, construct_id="KinesisTest", messaging_type="Kinesis"
        )
        kinesis_efo_test = KinesisEfoTest(
            scope=self,
            construct_id="KinesisEfoTest",
            messaging_type="Kinesis Enhanced Fan Out",
        )
        self.dashboard_obj = {"widgets": []}
        self.add_widgets_to_dashboard(sqs_test.messaging_type)
        self.add_widgets_to_dashboard(sqs_fifo_test.messaging_type)
        self.add_widgets_to_dashboard(sns_test.messaging_type)
        self.add_widgets_to_dashboard(sns_fifo_test.messaging_type)
        self.add_widgets_to_dashboard(sfn_standard_test.messaging_type)
        self.add_widgets_to_dashboard(sfn_express_test.messaging_type)
        self.add_widgets_to_dashboard(event_bridge_test.messaging_type)
        self.add_widgets_to_dashboard(kinesis_test.messaging_type)
        self.add_widgets_to_dashboard(kinesis_efo_test.messaging_type)
        cloudwatch.CfnDashboard(
            scope=self, id="Dashboard", dashboard_body=json.dumps(self.dashboard_obj)
        )

    def add_widgets_to_dashboard(self, messaging_type: str):
        # For every type, add a Text Header Widget
        self.dashboard_obj["widgets"].append(
            {
                "height": 1,
                "width": 24,
                "type": "text",
                "properties": {"markdown": f"# {messaging_type}"},
            },
        )
        # Then create the metrics for the SingleValue Widget
        metrics = [
            [
                "Serverless Messaging",
                "Latency",
                "Messaging Type",
                messaging_type,
                "Cold Start",
                "False",
                {
                    "yAxis": "left",
                    "label": f"{messaging_type} P{percentile} Latency",
                    "stat": f"p{percentile}",
                    "id": f"m{i}",
                },
            ]
            for i, percentile in enumerate(PERCENTILES)
        ]
        metrics += [
            [
                "...",
                {
                    "yAxis": "left",
                    "stat": "SampleCount",
                    "label": "Sample Count",
                    "id": f"m{len(PERCENTILES)}",
                },
            ]
        ]
        # And finally create the SingleValue Widget
        self.dashboard_obj["widgets"].append(
            {
                "height": 3,
                "width": 24,
                "type": "metric",
                "properties": {
                    "sparkline": False,
                    "metrics": metrics,
                    "view": "singleValue",
                    "stacked": False,
                    "region": "eu-west-1",
                    "stat": "p99",
                    "liveData": True,
                    "title": f"{messaging_type} Latency",
                    "setPeriodToTimeRange": True,
                    "trend": False,
                },
            }
        )
