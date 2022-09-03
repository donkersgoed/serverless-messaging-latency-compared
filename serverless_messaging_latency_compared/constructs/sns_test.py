# Third party imports
from aws_cdk import (
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
)
from constructs import Construct

from serverless_messaging_latency_compared.constructs.lambda_log_group import (
    LambdaLogGroup,
)

from serverless_messaging_latency_compared.constructs.invoker import (
    Invoker,
)


class SnsTest(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        topic = sns.Topic(scope=self, id="Topic")

        producer_lambda_function = lambda_.Function(
            scope=self,
            id="ProducerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/sns/producer/"),
            environment={"SNS_TOPIC_ARN": topic.topic_arn},
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

        topic.grant_publish(producer_lambda_function)

        consumer_lambda_function = lambda_.Function(
            scope=self,
            id="ConsumerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/sns/consumer/"),
            memory_size=3072,
            handler="index.event_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
        )
        LambdaLogGroup(
            scope=self,
            construct_id="ConsumerLogGroup",
            lambda_function=consumer_lambda_function,
        )

        topic.add_subscription(
            sns_subscriptions.LambdaSubscription(fn=consumer_lambda_function)
        )

        Invoker(
            scope=self, construct_id="Invoker", lambda_function=producer_lambda_function
        )
