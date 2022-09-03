# Third party imports
from aws_cdk import (
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_lambda as lambda_,
)
from constructs import Construct

OUTER_LOOP_SIZE = 32  # 32 * 32 = 1024 invocations
INNER_LOOP_SIZE = 32


class Invoker(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_function: lambda_.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        inner_parallel = sfn.Parallel(scope=self, id="32 Function Executions")
        for x in range(INNER_LOOP_SIZE):
            inner_parallel.branch(
                sfn_tasks.LambdaInvoke(
                    scope=self,
                    id=f"Lambda Invocation {x}",
                    lambda_function=lambda_function,
                    invocation_type=sfn_tasks.LambdaInvocationType.EVENT,
                )
            )

        inner_state_machine = sfn.StateMachine(
            scope=self,
            id="InnerStateMachine",
            definition=inner_parallel,
            state_machine_type=sfn.StateMachineType.STANDARD,
        )

        outer_parallel = sfn.Parallel(
            scope=self, id="32 Inner State Machine Executions"
        )

        for x in range(OUTER_LOOP_SIZE):
            outer_parallel.branch(
                sfn_tasks.StepFunctionsStartExecution(
                    scope=self,
                    id=f"Execute Inner State Machine {x}",
                    state_machine=inner_state_machine,
                    integration_pattern=sfn.IntegrationPattern.REQUEST_RESPONSE,
                ),
            )

        sfn.StateMachine(
            scope=self,
            id="OuterStateMachine",
            definition=outer_parallel,
            state_machine_type=sfn.StateMachineType.STANDARD,
        )
