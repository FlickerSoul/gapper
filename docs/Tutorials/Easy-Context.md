# (Easy) Context

Sometimes, you might want to capture some definitions in students' submissions for testing purposes. For example, suppose student writes a class `Car` that uses their definition of `GasStation`. You might want to reference the `GasStation` class when overriding tests. 

Note that you can access captured context only in the `gap_override_test` and any tests' pre hooks or post hooks. 

## Learn by Example

Suppose we are creating a problem that asks students to implement a function `add` that adds two numbers, using a given `adder` function. 
The required `adder` implementation is add two numbers and mod the result by 10. Below, we first define the golden solution adder named `my_adder`, and a custom testing 
function `custom_test` that uses the captured context, and the problem solution where the context is specified.

```python
from gapper import problem, test_case, test_cases
from gapper.core.unittest_wrapper import TestCaseWrapper
from gapper.core.test_result import TestResult

from typing import Callable

# my_adder is a solution adder defined along with the solution
def my_adder(a, b) -> int:
    return a + b % 10


# variable `adder` is not defined here, this is just a type hint
# the name `adder` will be specified in the context to be captured 
# see the last comment in this code
# and the name `adder` will become available to custom override
# testing function or the pre-/post-hooks
adder: Callable[[int, int], int]


# custom test that uses the captured context
def custom_test(case: TestCaseWrapper, result_proxy: TestResult, solution, submission):
    assert my_adder(*case.test_param.args) == adder(*case.test_param.args) # notice here
    # adder is not defined, but we can use it
    # this is because it will be captured from students' submission context
    
    # test if student's adder behaves the same in the solution as in their submission
    assert solution(*case.test_param.args, adder) == submission(
        *case.test_param.args,
        case.context.adder,  # access adder from test case
    )
    

@test_cases.param_iter(([i, i + 1] for i in range(10)), gap_override_test=custom_test)
@test_case(1, 2, gap_override_test=custom_test)
# we specify the name of the context to be captured
# easy_context is the flag that allows `add` to be used even though it's not defined
@problem(context=["adder"], easy_context=True) 
def add(a: int, b: int, the_adder: Callable[[int, int], int]) -> int:
    return the_adder(a, b)
```

Thus if the student's submission is 

```python
def adder(a, b):
    return (a % 10 + b % 10) % 10

def add(a, b, some_adder):
    return some_adder(a, b)
```

The test will pass because the student's `adder` is semantically equivalent to the solution's `my_adder`.

The `easy_context` flag, which is set to `True` by default, in the `@problem` decorator allows you to inject context variables directly. In the example above, you can use `add` even though it's not defined. If `easy_context` is set to False, you can still access the captured context using `case.context.<context_variable_name>`. For example, `case.context.adder`

If any of the names specified in `context` is not present in student's submission, the submission will be rejected without testing. 

That is, in the example above, if the student's submission is 

```python
def add(a, b):
    return (a % 10 + b % 10) % 10
```
, because the file does not contain `adder`, it will be rejected. 
