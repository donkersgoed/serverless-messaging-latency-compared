# Third party imports
from aws_cdk import (
    Fn,
    RemovalPolicy,
    aws_logs as logs,
    aws_lambda as lambda_,
)
from constructs import Construct


class LambdaLogGroup(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_function: lambda_.Function,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        logs.LogGroup(
            scope=self,
            id="LogGroup",
            retention=logs.RetentionDays.ONE_DAY,
            log_group_name=Fn.sub(
                "/aws/lambda/${Function}",
                {"Function": lambda_function.function_name},
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
