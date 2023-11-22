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

The functions to `gap_override_test`, `gap_post_hooks`, `gap_pre_hooks`, `pre_tests` and `post_tests` all need an input of `TestResult` type. See [this page](./Various-Function-Protocols.md) for their signatures. 

You can set the result attributes using `set_<attribute>()` function. For example, 

```python
result_proxy.set_score(result_proxy.max_score // 2)
result_proxy.set_pass_status("failed")
result_proxy.add_description(
    "Failed because recursive call not found in submission."
)
```

Please refer to the API reference [here](https://gapper.universe.observer/API/test_result/) for detailed usages. 