# Third party imports
from platform import node
from aws_cdk import (
    Fn,
    aws_lambda as lambda_,
    aws_events as events,
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


class EventBridgeTest(Construct):
    def __init__(
        self, scope: Construct, construct_id: str, messaging_type: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.messaging_type = messaging_type

        consumer_lambda_function = lambda_.Function(
            scope=self,
            id="ConsumerFunction",
            code=lambda_.Code.from_asset(
                path="lambda_/functions/eventbridge/consumer/"
            ),
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

        event_bus = events.EventBus(
            scope=self,
            id="TestEventBus",
            event_bus_name="TestEventBus",
        )

        rule = events.CfnRule(
            scope=self,
            id="Rule",
            name="MonitoringConsumer",
            event_bus_name=event_bus.event_bus_name,
            event_pattern={"account": [Fn.ref("AWS::AccountId")]},
            targets=[
                events.CfnRule.TargetProperty(
                    arn=consumer_lambda_function.function_arn,
                    id="LambdaTarget",
                ),
            ],
        )

        # Allow rule to invoke lambda
        consumer_lambda_function.add_permission(
            id="RulePermission",
            principal=iam.ServicePrincipal("events.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=rule.attr_arn,
        )

        producer_lambda_function = lambda_.Function(
            scope=self,
            id="ProducerFunction",
            code=lambda_.Code.from_asset(
                path="lambda_/functions/eventbridge/producer/"
            ),
            environment={"EVENT_BUS_NAME": event_bus.event_bus_name},
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

        event_bus.grant_all_put_events(producer_lambda_function)

        Invoker(
            scope=self, construct_id="Invoker", lambda_function=producer_lambda_function
        )
