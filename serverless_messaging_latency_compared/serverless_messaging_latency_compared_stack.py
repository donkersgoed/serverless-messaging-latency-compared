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
from serverless_messaging_latency_compared.constructs.sfn_standard_test import (
    SfnStandardTest,
)
from serverless_messaging_latency_compared.constructs.sfn_express_test import (
    SfnExpressTest,
)
from serverless_messaging_latency_compared.constructs.eventbridge_test import (
    EventBridgeTest,
)


class ServerlessMessagingLatencyComparedStack(Stack):
    """The ServerlessMessagingLatencyCompared Stack."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Construct a new ServerlessMessagingLatencyComparedStack."""
        super().__init__(scope, construct_id, **kwargs)

        SqsTest(scope=self, construct_id="SqsTest")
        SnsTest(scope=self, construct_id="SnsTest")
        KinesisTest(scope=self, construct_id="KinesisTest")
        SfnStandardTest(scope=self, construct_id="SfnStandardTest")
        SfnExpressTest(scope=self, construct_id="SfnExpressTest")
        EventBridgeTest(scope=self, construct_id="EventBridgeTest")
