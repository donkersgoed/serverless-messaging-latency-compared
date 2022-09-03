# Third party imports
from aws_cdk import (
    Fn,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_logs as logs,
)
from constructs import Construct

from serverless_messaging_latency_compared.constructs.lambda_log_group import (
    LambdaLogGroup,
)

from serverless_messaging_latency_compared.constructs.invoker import (
    Invoker,
)


class SqsTest(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(scope=self, id="TestQueue")

        producer_lambda_function = lambda_.Function(
            scope=self,
            id="ProducerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/sqs/producer/"),
            environment={"SQS_QUEUE_URL": queue.queue_url},
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

        queue.grant_send_messages(producer_lambda_function)

        consumer_lambda_function = lambda_.Function(
            scope=self,
            id="ConsumerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/sqs/consumer/"),
            memory_size=3072,
            handler="index.event_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
        )
        LambdaLogGroup(
            scope=self,
            construct_id="ConsumerLogGroup",
            lambda_function=consumer_lambda_function,
        )

        queue.grant_consume_messages(consumer_lambda_function)

        consumer_lambda_function.add_event_source_mapping(
            id="QueueESM", batch_size=1, event_source_arn=queue.queue_arn
        )

        Invoker(
            scope=self, construct_id="Invoker", lambda_function=producer_lambda_function
        )