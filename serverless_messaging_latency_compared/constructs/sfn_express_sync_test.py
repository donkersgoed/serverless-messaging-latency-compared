# Third party imports
from aws_cdk import (
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
)
from constructs import Construct

# Local application/library specific imports
from serverless_messaging_latency_compared.constructs.lambda_log_group import (
    LambdaLogGroup,
)
from serverless_messaging_latency_compared.constructs.invoker import (
    Invoker,
)


class SfnExpressSyncTest(Construct):
    def __init__(
        self, scope: Construct, construct_id: str, messaging_type: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.messaging_type = messaging_type

        consumer_lambda_function = lambda_.Function(
            scope=self,
            id="ConsumerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/sfn/consumer/"),
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

        state_machine = sfn.StateMachine(
            scope=self,
            id="TestMachine",
            definition=sfn_tasks.LambdaInvoke(
                scope=self,
                id=f"Lambda Invocation",
                lambda_function=consumer_lambda_function,
                invocation_type=sfn_tasks.LambdaInvocationType.REQUEST_RESPONSE,
            ),
            state_machine_type=sfn.StateMachineType.EXPRESS,
        )

        producer_lambda_function = lambda_.Function(
            scope=self,
            id="ProducerFunction",
            code=lambda_.Code.from_asset(path="lambda_/functions/sfn/producer/"),
            environment={"STATE_MACHINE_ARN": state_machine.state_machine_arn},
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

        state_machine.grant_start_execution(producer_lambda_function)

        Invoker(
            scope=self, construct_id="Invoker", lambda_function=producer_lambda_function
        )
