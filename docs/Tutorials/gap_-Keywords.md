# `gap_` Keywords

This post discusses the effect of each `gap_` keyword and how they can be used. 

## `gap_` Keyword Listing

We list the possible `gap_` keywords below. 

```text
gap_expect: The expected output of the test case.
gap_expect_stdout: The expected stdout of the test case.
gap_hidden: Whether the test case is hidden.
gap_name: The name of the test case.
gap_extra_points: The extra credit of the test case.
gap_override_check: The custom equality check function.
gap_override_test: The custom test function.
gap_post_checks: The custom post check functions.
gap_description: The description of the test case.
gap_is_pipeline: Whether the test case is a pipeline.
gap_max_score: The max score of the test case. This and gap_weight cannot be specified as the same time. 
gap_weight: The weight of the test case. This and gap_max_score cannot be specified as the same time. 
```

## How To Specify Them In `@test_case()` And `@test_cases`

- In `@test_case()`, `gap_` keywords are specified as ordinary keyword arguments. For example, `@test_case(1, 2, gap_expect=3, gap_name="secret test", gap_max_score=5)`. 
- In `@test_cases()`, `gap_` keywords are also specified as keyword arguments but accept one single value or a `Sequence` of values. For example, `@test_cases.params([1,2], [3,4], gap_max_score=2, gap_name=["test 1", "test 2"])`. When a single value is passed, it will be duplicated to every test cases. When a sequence is passed, the length of the sequence has to be the same as the number of test cases, and will be applied to each test case in order. 

## `gap_expect` 

This serves as sanity check to the correctness of the defined problem. When specified in a test case, it's value equals the expected outcome of executing the test case. For example, 

```python
# add_num.py
@test_case(2, 2, gap_expect=3)
@test_case(1, 2, gap_expect=3)
@problem()
def add(a: int, b: int) -> int:
    return a + b
```

Using the command line, we invoke `gapper check add_num.py` ad we will see 

```shell
❯ gapper check add_num.py
Test (1, 2) passed: True
Test (2, 2) passed: False
  result: 4
  expected result: 3
  output: None
  expected output: None
```

## `gap_expect_stdout`

It is similar to `gap_expect` except it expects output from the `stdout`. 

## `gap_hidden` 

It accepts `True` or `False` and indicates if the test case can be seen by student. For example, 

```python
@test_cases.param_iter(
    ([random.randint(100, 10000)] for _ in range(3)),
    gap_max_score=2,
    gap_hidden=True,
    gap_name="random hidden tests",
)
```
 will make the entries not shown to students at all (but still visible from instructor/TA's panel)

![image](https://github.com/FlickerSoul/gapper/assets/13360148/e5484532-b310-438e-8428-1c20deaa5b90)


## `gap_name` 

A custom name of the autograder beside showing the argument passed to the test. For example, 

```python
@test_cases.param_iter(
    ([random.randint(100, 10000)] for _ in range(3)),
    gap_max_score=2,
    gap_hidden=True,
    gap_name="random hidden tests",
)
@test_cases.param_iter(
    ([random.randint(100, 10000)] for _ in range(3)),
    gap_max_score=0,
    gap_name="random tests",
)
```

will produce 

![image](https://github.com/FlickerSoul/gapper/assets/13360148/98f6c866-6b8c-480b-a6f1-3f84edddce48)

## `gap_description`

Description of the test that will be shown to the students. For example, the following code will produce the result below. 

```python
@test_case(
    1, gap_max_score=1, gap_description="this is the test in the assignment handout"
)
@test_case(1234, gap_max_score=1, gap_description=["this test is ", "slightly longer"])
```

![image](https://github.com/FlickerSoul/gapper/assets/13360148/4a15fe41-b652-4dbd-8139-b0e28b841e1b)


## `gap_max_score` 

The max score this test is worth. This cannot coexist with `gap_weight`. 

## `gap_weight`

The weight of the max score this test is worth. This cannot coexist with `gap_max_score`. The calculation of the max score is 

```
max_score_of_the_test = gap_weight * (totoal_score_of_the_assignment - sum(gap_max_score in all tests)) / sum(gap_weight in all tests) 
```

If both `gap_weight` and `gap_max_score` are not set, the test case will be assigned with a default weight of `1`. 

For example, suppose we create 4 test cases worth total 4 points. 

```python
@test_case(1, gap_description="this is the test in the assignment handout")
@test_case(1234, gap_weight=2, gap_description=["this test is ", "slightly longer"])
@test_case(3731, gap_weight=4)
@test_case(7)
```

will produce the following max score assignment 

![image](https://github.com/FlickerSoul/gapper/assets/13360148/93ae3738-6b4f-48f4-a91f-b11a24d49be3)

because, for the test case of `(1,)` and case of `(7,)`, the score is calculated as 

```
1 * (4 - 0) / (1 + 2 + 4 + 1) = 4 / 8 = 0.5
```

and similarly, the score assigned for the case of `(1234,)` is from 

```
2 * (4 - 0) / (1 + 2 + 4 + 1) = 8 / 8 = 1
```

## `gap_extra_points`

Extra points specified in a test is a number and will be granted to student if they passed to test. For example, 

```python
@test_case(random.randint(100000, 1000000), gap_max_score=0, gap_extra_points=5)
```

will result in 5 extra points when the student passes the test, shown as following: 

![image](https://github.com/FlickerSoul/gapper/assets/13360148/1ee6f2d3-dd26-4001-9ead-e5b7845e3a59)


## `gap_override_check`

You can override tests' equality checks by passing a comparator function to `gap_override_check` keyword. 

For example, suppose the you want to compare answers from students' submissions with the solution but do not care about ordering, you can pass 
`gap_override_check=set_equality` to `@test_case()` where `set_equality` is pre-defined in your script as 

```python
def set_equality(solution_answer: Any, submission_answer: Any) -> bool:
    return set(solution_answer) == set(submission_answer)
```

## `gap_override_test`

You can override entire test by passing a custom function to `gap_override_test` parameter, similar to override equality checks. For example, you not only want to check the answers, but also ensure the function is recursive. You can define `custom_test` as the following and pass it as `gap_override_test=custom_test` in your `@test_case()`. Note that you have to run the test and equality check by yourself, for the entire test process is overridden. 

```python
from gapper import problem, test_case
from gapper.core.test_result import TestResult
from gapper.core.unittest_wrapper import TestCaseWrapper


def check_recursive_ast(fn):
    tree = ast.parse(inspect.getsource(fn))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == fn.__name__:
                    return True
    return False

def custom_test(param: TestCaseWrapper, result_proxy: TestResult, solution, submission) -> bool:
    soln_ans = solution(*param.args, **param.kwargs)
    subm_ans = submission(*param.args, **param.kwargs)

    param.assertEqual(soln_ans, subm_ans)  # equivalent to `assert soln_ans == subm_ans`
    
    # param.assertTrue(check_recursive_ast(submission))
    # equivalent to `assert check_recursive_ast(submission)`

    if not check_recursive_ast(submission):
        result_proxy.set_score(result_proxy.max_score // 2)

@test_case(10, gap_override_test=custom_test)
@problem()
def fib(n: int) -> int:
    ...
```

A overriding function show have the following positional parameter signature 

```python

class CustomTestFn(Protocol):
    def __call__[T](self, param: TestCaseWrapper, result_proxy: TestResult, expected: T, actual: T) -> None:
        ...
```

## `gap_post_checks`

Consider the situation in which you'd like to provide extra checks but not override the whole test. You can write custom check functions and pass it into `gap_post_checks`. For example, you'd like to check if the students' solutions are recursive, you can write 

```python
from gapper import problem, test_case
from gapper.core.test_result import TestResult
from gapper.core.unittest_wrapper import TestCaseWrapper


def check_recursive_ast(fn):
    tree = ast.parse(inspect.getsource(fn))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == fn.__name__:
                    return True
    return False

def recursive_check(param: TestCaseWrapper, result_proxy: TestResult, solution, submission, sln_results: Tuple[Any, str | None], sub_results: Tuple[Any, str | None]) -> None:
    if not check_recursive_ast(submission):
        result_proxy.set_score(result_proxy.max_score // 2)
        result_proxy.set_pass_status("failed")
        result_proxy.add_description(
            "Failed because recursive call not found in submission."
        )

@test_case(10, gap_post_check=recursive_check)
@problem()
def fib(n: int) -> int:
    ...
```

A post check function has to follow the following positional parameter signature

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

## `gap_pipeline` 

The `gap_pipeline` keyword is invented to simulated a sequence of actions acting on an object. The object going into the pipeline might remain the same, be modified, or be swapped. It comes handy when testing classes and their instances' behaviors. For example, given a `Car` class, 

```python
class Car:
    def __init__(self, x: int, y: int, tank_size: float) -> None:
        self.x = x
        self.y = y
        self.tank_size = tank_size
        self.fuel = tank_size

    def drive_to(self, x: int, y: int) -> bool:
        dis = abs(x - self.x) + abs(y - self.y)
        if dis > self.fuel:
            return False
        else:
            self.fuel -= dis
            self.x = x
            self.y = y
            return True

    def refill(self) -> None:
        self.fuel = self.tank_size

    def get_fuel(self) -> float:
        return self.fuel
```

Using pipeline, we can (1) test creating instances with different parameters, (2) running some functions of the instances and check if their outputs match, (3) and checking if attributes and states match (but we recommend requiring student to create uniform interfaces (functions) and not check the properties directly). 

```python
from gapper import problem, test_case
from gapper.core.pipeline_support import Constructor, Function, Property

init = Constructor()
drive_to = Function("drive_to")
refill = Function("refill")
get_fuel = Function("get_fuel")
x = Property("x")
y = Property("y")
tank_size = Property("tank_size")


@test_case.pipeline(   # using `@test_case.pipeline` is equivalent to `@test_case(gap_pipeline=True)`
    init(0, 0, 100),
    tank_size,         # we recommend creating a uniform interface such as `get_tank_size()`
    x,                 # and not to check the attributes directly 
    y,
    drive_to(10, 10),
    get_fuel(),
    drive_to(100, 0),
    get_fuel(),
    refill(),
    drive_to(100, 0),
    get_fuel(),
)
@problem()
class Car:
    ...
```

## Example Script 

```python
from gapper import problem, test_case, test_cases
import random


@test_case(random.randint(100000, 1000000), gap_max_score=0, gap_extra_points=5)
@test_cases.param_iter(
    ([random.randint(100, 10000)] for _ in range(3)),
    gap_max_score=2,
    gap_hidden=True,
    gap_name="random hidden tests",
)
@test_cases.param_iter(
    ([random.randint(100, 10000)] for _ in range(3)),
    gap_max_score=0,
    gap_name="random tests",
)
@test_case(1, gap_description="this is the test in the assignment handout")
@test_case(1234, gap_weight=2, gap_description=["this test is ", "slightly longer"])
@test_case(3731, gap_weight=4)
@test_case(7)
@problem(check_stdout=True)
def print_digits(n: int) -> None:
    print(n % 10)
    if n >= 10:
        print_digits(n // 10)
```