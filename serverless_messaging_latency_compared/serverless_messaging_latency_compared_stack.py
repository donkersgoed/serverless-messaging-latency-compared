"""Module for the main ServerlessMessagingLatencyCompared Stack."""

# Third party imports
from aws_cdk import (
    Stack,
)
from constructs import Construct

# Local application/library specific imports
from serverless_messaging_latency_compared.constructs.sqs_test import SqsTest
from serverless_messaging_latency_compared.constructs.sns_test import SnsTest
from serverless_messaging_latency_compared.constructs.kinesis_test import KinesisTest


class ServerlessMessagingLatencyComparedStack(Stack):
    """The ServerlessMessagingLatencyCompared Stack."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Construct a new ServerlessMessagingLatencyComparedStack."""
        super().__init__(scope, construct_id, **kwargs)

        SqsTest(scope=self, construct_id="SqsTest")
        SnsTest(scope=self, construct_id="SnsTest")
        KinesisTest(scope=self, construct_id="KinesisTest")
