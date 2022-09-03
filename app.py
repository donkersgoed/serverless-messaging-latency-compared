#!/usr/bin/env python3

# Third party imports
import aws_cdk as cdk

# Local application/library specific imports
from serverless_messaging_latency_compared.serverless_messaging_latency_compared_stack import (
    ServerlessMessagingLatencyComparedStack,
)


app = cdk.App()
ServerlessMessagingLatencyComparedStack(
    scope=app,
    construct_id="ServerlessMessagingLatencyComparedStack",
)

app.synth()
