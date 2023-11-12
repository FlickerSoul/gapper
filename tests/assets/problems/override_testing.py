from gapper import problem, test_case, test_cases
from gapper.core.unittest_wrapper import TestCaseWrapper


class PrivateTestingMiddleware:
    def __init__(self, secret: str) -> None:
        self.secret = secret

    def respond(self, response: str) -> str:
        return response * 2 + self.secret


def custom_test(param: TestCaseWrapper, result_proxy, solution, submission) -> None:
    standard_middleware = param.context.StandardMiddleware()
    standard_sln = solution(standard_middleware)
    standard_sub = submission(standard_middleware)
    for test_response in param.test_param.args:
        assert standard_sln.generate_middleware_response(
            test_response
        ) == standard_sub.generate_middleware_response(test_response)

    private_middleware = PrivateTestingMiddleware("the secret")
    private_sln = solution(private_middleware)
    private_sub = submission(private_middleware)

    for test_response in param.test_param.args:
        assert private_sln.generate_middleware_response(
            test_response
        ) == private_sub.generate_middleware_response(test_response)


@test_cases.params(
    [chr(i + ord("a")) for i in range(5)],
    [chr(i + ord("A")) for i in range(5)],
    [chr(ord("Z") - i) for i in range(5)],
    gap_override_test=custom_test,
)
@test_case("a", "bb", "ccc", gap_override_test=custom_test)
@problem(context=["StandardMiddleware"])
class Factory:
    def __init__(self, middleware) -> None:
        self.middleware = middleware

    def generate_middleware_response(self, response: str) -> str:
        return self.middleware.respond(response) + "\n" + "end$"


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": ["StandardMiddleware"],
    "easy_context": False,
    "gs_connect": None,
}
