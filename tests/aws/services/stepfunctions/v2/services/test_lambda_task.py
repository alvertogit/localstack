import json

import pytest
from localstack_snapshot.snapshots.transformer import RegexTransformer

from localstack.aws.api.lambda_ import Runtime
from localstack.testing.pytest import markers
from localstack.testing.pytest.stepfunctions.utils import (
    create_and_record_execution,
)
from localstack.utils.strings import short_uid
from tests.aws.services.stepfunctions.lambda_functions import lambda_functions
from tests.aws.services.stepfunctions.templates.services.services_templates import (
    ServicesTemplates as ST,
)


class TestTaskLambda:
    @markers.aws.validated
    def test_invoke_bytes_payload(
        self,
        aws_client,
        create_state_machine_iam_role,
        create_state_machine,
        create_lambda_function,
        sfn_snapshot,
    ):
        function_1_name = f"lambda_1_func_{short_uid()}"
        create_1_res = create_lambda_function(
            func_name=function_1_name,
            handler_file=ST.LAMBDA_RETURN_BYTES_STR,
            runtime=Runtime.python3_12,
        )
        sfn_snapshot.add_transformer(RegexTransformer(function_1_name, "<lambda_function_1_name>"))

        template = ST.load_sfn_template(ST.LAMBDA_INVOKE_RESOURCE)
        template["States"]["step1"]["Resource"] = create_1_res["CreateFunctionResponse"][
            "FunctionArn"
        ]
        definition = json.dumps(template)

        exec_input = json.dumps({})
        create_and_record_execution(
            aws_client,
            create_state_machine_iam_role,
            create_state_machine,
            sfn_snapshot,
            definition,
            exec_input,
        )

    @markers.aws.validated
    def test_invoke_string_payload(
        self,
        aws_client,
        create_state_machine_iam_role,
        create_state_machine,
        create_lambda_function,
        sfn_snapshot,
    ):
        function_1_name = f"lambda_1_func_{short_uid()}"
        create_1_res = create_lambda_function(
            func_name=function_1_name,
            handler_file=ST.LAMBDA_ID_FUNCTION,
            runtime=Runtime.python3_12,
        )
        sfn_snapshot.add_transformer(RegexTransformer(function_1_name, "<lambda_function_1_name>"))

        template = ST.load_sfn_template(ST.LAMBDA_INVOKE_RESOURCE)
        template["States"]["step1"]["Resource"] = create_1_res["CreateFunctionResponse"][
            "FunctionArn"
        ]
        definition = json.dumps(template)

        exec_input = json.dumps("HelloWorld")
        create_and_record_execution(
            aws_client,
            create_state_machine_iam_role,
            create_state_machine,
            sfn_snapshot,
            definition,
            exec_input,
        )

    @pytest.mark.parametrize(
        "json_value",
        [
            "HelloWorld",
            0.0,
            0,
            -0,
            True,
            {},
            [],
        ],
    )
    @markers.aws.validated
    def test_invoke_json_values(
        self,
        aws_client,
        create_state_machine_iam_role,
        create_state_machine,
        create_lambda_function,
        sfn_snapshot,
        json_value,
    ):
        function_1_name = f"lambda_1_func_{short_uid()}"
        create_1_res = create_lambda_function(
            func_name=function_1_name,
            handler_file=ST.LAMBDA_ID_FUNCTION,
            runtime=Runtime.python3_12,
        )
        sfn_snapshot.add_transformer(RegexTransformer(function_1_name, "<lambda_function_1_name>"))

        template = ST.load_sfn_template(ST.LAMBDA_INVOKE_RESOURCE)
        template["States"]["step1"]["Resource"] = create_1_res["CreateFunctionResponse"][
            "FunctionArn"
        ]
        definition = json.dumps(template)

        exec_input = json.dumps(json_value)
        create_and_record_execution(
            aws_client,
            create_state_machine_iam_role,
            create_state_machine,
            sfn_snapshot,
            definition,
            exec_input,
        )

    @markers.aws.validated
    def test_invoke_pipe(
        self,
        aws_client,
        create_state_machine_iam_role,
        create_state_machine,
        create_lambda_function,
        sfn_snapshot,
    ):
        function_1_name = f"lambda_1_func_{short_uid()}"
        create_1_res = create_lambda_function(
            func_name=function_1_name,
            handler_file=lambda_functions.ECHO_FUNCTION,
            runtime=Runtime.python3_12,
        )
        sfn_snapshot.add_transformer(RegexTransformer(function_1_name, "<lambda_function_1_name>"))

        function_2_name = f"lambda_2_func_{short_uid()}"
        create_2_res = create_lambda_function(
            func_name=function_2_name,
            handler_file=lambda_functions.ECHO_FUNCTION,
            runtime=Runtime.python3_12,
        )
        sfn_snapshot.add_transformer(RegexTransformer(function_2_name, "<lambda_function_2_name>"))

        template = ST.load_sfn_template(ST.LAMBDA_INVOKE_PIPE)
        template["States"]["step1"]["Resource"] = create_1_res["CreateFunctionResponse"][
            "FunctionArn"
        ]
        template["States"]["step2"]["Resource"] = create_2_res["CreateFunctionResponse"][
            "FunctionArn"
        ]
        definition = json.dumps(template)

        exec_input = json.dumps({})
        create_and_record_execution(
            aws_client,
            create_state_machine_iam_role,
            create_state_machine,
            sfn_snapshot,
            definition,
            exec_input,
        )

    @markers.aws.validated
    def test_lambda_task_filter_parameters_input(
        self,
        aws_client,
        create_state_machine_iam_role,
        create_state_machine,
        create_lambda_function,
        sfn_snapshot,
    ):
        function_name = f"lambda_func_{short_uid()}"
        create_res = create_lambda_function(
            func_name=function_name,
            handler_file=ST.LAMBDA_ID_FUNCTION,
            runtime=Runtime.python3_12,
        )
        sfn_snapshot.add_transformer(RegexTransformer(function_name, "lambda_function_name"))
        function_arn = create_res["CreateFunctionResponse"]["FunctionArn"]

        template = ST.load_sfn_template(ST.LAMBDA_INPUT_PARAMETERS_FILTER)
        template["States"]["CheckComplete"]["Resource"] = function_arn
        definition = json.dumps(template)

        exec_input = json.dumps({})
        create_and_record_execution(
            aws_client,
            create_state_machine_iam_role,
            create_state_machine,
            sfn_snapshot,
            definition,
            exec_input,
        )
