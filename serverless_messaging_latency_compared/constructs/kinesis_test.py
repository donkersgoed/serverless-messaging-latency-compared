# Third party imports
from aws_cdk import (
    aws_lambda as lambda_,
    aws_kinesis as kds,
)
from constructs import Construct

# Local application/library specific imports
from serverless_messaging_latency_compared.constructs.lambda_log_group import (
    LambdaLogGroup,
)
from serverless_messaging_latency_compared.constructs.invoker import (
    Invoker,
)


class KinesisTest(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stream = kds.Stream(scope=self, id="TestStream", shard_count=1)

        producer_lambda_function = lambda_.Function(
            scope=self,
            id="ProducerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/kinesis/producer/"),
            environment={"KDS_STREAM_NAME": stream.stream_name},
            memory_size=3072,
            handler="index.event_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            reserved_concurrent_executions=1,
        )
        LambdaLogGroup(
            scope=self,
            construct_id="ProducerLogGroup",
            lambda_function=producer_lambda_function,
        )

        stream.grant_write(producer_lambda_function)

        consumer_lambda_function = lambda_.Function(
            scope=self,
            id="ConsumerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/kinesis/consumer/"),
            environment={"MESSAGING_TYPE": "Kinesis"},
            memory_size=3072,
            handler="index.event_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
        )
        LambdaLogGroup(
            scope=self,
            construct_id="ConsumerLogGroup",
            lambda_function=consumer_lambda_function,
        )

        stream.grant_read(consumer_lambda_function)

        consumer_lambda_function.add_event_source_mapping(
            id="StreamESM",
            batch_size=1,
            event_source_arn=stream.stream_arn,
            starting_position=lambda_.StartingPosition.LATEST,
        )

        Invoker(
            scope=self, construct_id="Invoker", lambda_function=producer_lambda_function
        )
