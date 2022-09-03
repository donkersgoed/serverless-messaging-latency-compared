"""Module for the main ServerlessMessagingLatencyCompared Stack."""

# Third party imports
from aws_cdk import (
    Stack,
)
from constructs import Construct


class ServerlessMessagingLatencyComparedStack(Stack):
    """The ServerlessMessagingLatencyCompared Stack."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Construct a new ServerlessMessagingLatencyComparedStack."""
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
