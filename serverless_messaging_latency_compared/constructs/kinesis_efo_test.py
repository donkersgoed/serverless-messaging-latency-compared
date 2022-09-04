# Third party imports
from aws_cdk import (
    Fn,
    aws_lambda as lambda_,
    aws_kinesis as kds,
    aws_iam as iam,
)
from constructs import Construct

# Local application/library specific imports
from serverless_messaging_latency_compared.constructs.lambda_log_group import (
    LambdaLogGroup,
)
from serverless_messaging_latency_compared.constructs.invoker import (
    Invoker,
)


class KinesisEfoTest(Construct):
    def __init__(
        self, scope: Construct, construct_id: str, messaging_type: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.messaging_type = messaging_type

        stream = kds.Stream(scope=self, id="TestStream", shard_count=1)
        kds_consumer = kds.CfnStreamConsumer(
            scope=self,
            id="EfoConsumer",
            consumer_name="consumer",
            stream_arn=stream.stream_arn,
        )

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
            environment={"MESSAGING_TYPE": messaging_type},
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
            event_source_arn=kds_consumer.attr_consumer_arn,
            starting_position=lambda_.StartingPosition.LATEST,
        )

        consumer_lambda_function.role.add_to_principal_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["kinesis:SubscribeToShard"],
                resources=[kds_consumer.attr_consumer_arn],
            )
        )

        Invoker(
            scope=self, construct_id="Invoker", lambda_function=producer_lambda_function
        )
