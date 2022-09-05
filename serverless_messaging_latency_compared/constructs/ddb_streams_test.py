# Third party imports
from aws_cdk import (
    aws_lambda as lambda_,
    aws_dynamodb as ddb,
)
from constructs import Construct

# Local application/library specific imports
from serverless_messaging_latency_compared.constructs.lambda_log_group import (
    LambdaLogGroup,
)
from serverless_messaging_latency_compared.constructs.invoker import (
    Invoker,
)


class DynamoDbStreamsTest(Construct):
    def __init__(
        self, scope: Construct, construct_id: str, messaging_type: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.messaging_type = messaging_type

        consumer_lambda_function = lambda_.Function(
            scope=self,
            id="ConsumerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/ddb/consumer/"),
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

        table = ddb.Table(
            scope=self,
            id="Table",
            partition_key=ddb.Attribute(name="PK", type=ddb.AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_IMAGE,
        )

        producer_lambda_function = lambda_.Function(
            scope=self,
            id="ProducerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/ddb/producer/"),
            environment={"DDB_TABLE_NAME": table.table_name},
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

        table.grant_read_write_data(producer_lambda_function)

        table.grant_stream_read(consumer_lambda_function)

        consumer_lambda_function.add_event_source_mapping(
            id="StreamESM",
            batch_size=1,
            event_source_arn=table.table_stream_arn,
            starting_position=lambda_.StartingPosition.LATEST,
        )

        Invoker(
            scope=self, construct_id="Invoker", lambda_function=producer_lambda_function
        )
