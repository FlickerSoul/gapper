# `TestResult` (Proxy)

We discuss how to operate the result proxy when overriding a test or writing custom post check functions. We recommend reading the [`gap_override_test`](https://github.com/FlickerSoul/gapper/wiki/gap_-Keywords#gap_override_test) and [`gap_post_checks`](https://github.com/FlickerSoul/gapper/wiki/gap_-Keywords#gap_post_checks) sections first. 

## Structure of `TestResult`(Proxy)

A `TestResult` contains information of the execution result of a test. Thus, when creating your own testing functions or post checking functions, you might want to modify the test result object accordingly to store information such as score obtained, pass status, descriptions of the test, etc. In the text below, we will use test result proxy and test result interchangeably. 

```python
@dataclass
class TestResult:
    default_name: str
    name: str | None = None
    score: float | None = field(default=None)
    max_score: float | None = field(default=None)
    weight: int | None = field(default=None)
    extra_points: float | None = field(default=None)
    errors: List[ErrorFormatter] = field(default_factory=list)
    pass_status: PassStateType | None = field(default=None)
    hidden: bool = False
    descriptions: List[str] = field(default_factory=list)
```

## Usage

The signature of a `gap_override_test` function and a `gap_post_check` function are the following, in which the second positional argument is the `TestResult` proxy.

```python

class CustomTestFn(Protocol):
    def __call__[T](self, param: TestCaseWrapper, result_proxy: TestResult, expected: T, actual: T) -> None:
        ...
```

```python
class PostChecksFn(Protocol):
    def __call__[T](
        self,
        param: TestCaseWrapper,
        result_proxy: TestResult,
        solution: T,
        submission: T,
        expected_results: Tuple[Any, str | None],
        actual_results: Tuple[Any, str | None],
    ) -> None:
        ...
```

You can set the result attributes using `set_<attribute>()` function. For example, 

```python
result_proxy.set_score(result_proxy.max_score // 2)
result_proxy.set_pass_status("failed")
result_proxy.add_description(
    "Failed because recursive call not found in submission."
)
```

Please refer to the API reference [here](https://gapper.universe.observer/API/test_result/) for detailed usages. 