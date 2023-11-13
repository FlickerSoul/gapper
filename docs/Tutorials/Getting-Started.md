# Getting Started

Welcome to `gapper` wiki. Here you can find how to use gapper and how to contribute to gapper. This project is inspired by [aga](https://github.com/rileyshahar/aga) and some core code is took from my contribution to the `aga` project. 

If you're looking for API references, please visit [this page](http://gapper.universe.observer/)

## Why `gapper` And Who Might Find It Helpful. 

`gapper` is created to facilitate creating autograders for the GradeScope platform. The official tool recommended by GradeScope is [`gradescope-utils`](https://github.com/gradescope/gradescope-utils). However, this tool requires users to write cumbersome `unittest` test cases like the following: 

```python
class TestSimpleArithmetic(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    @weight(1)
    def test_eval_add(self):
        """Evaluate 1 + 1"""
        val = self.calc.eval("1 + 1")
        self.assertEqual(val, 2)
```

Considering professors and teaching assistants usually provide their solutions to students, we created `gapper` to help them create graders directly and easily from the solutions, without writing boilerplates and test cases from the ground up. For example, the code above can be expressed as the following with the help from `gapper`:

```python
from gapper import problem, test_case
from gapper.core.pipeline_support import Constructor, Function, Property

init = Constructor()
eval = Function("eval")

@test_case.pipeline(init(), eval("1 + 1"))
@problem()
class Calculator:
    """The calculator solution."""
```

Note that we designed `gapper` to handle simple workflow, such as testing a single function, a single class, etc. You can adapt `gapper` to more complicated workflow by overriding test processes using `gap_override_test` which will be covered in a separate post. 

If you're interested, please check out the following workflow brief. 

## Workflow Brief

Suppose you are creating a autograder for the following Python solution:

```python
# print_digits.py
def print_digits(n: int) -> None:
    print(n % 10)
    if n >= 10:
        print_digits(n // 10)
```

First, you need to install `gapper` by running `pip install gapper` in your terminal (the minimal Python version is 3.12.0). Once it's installed, you can import `problem` from `gapper` and invoke it as a decorator, like the following. This will transform the solution into a problem operated by the autograder. The `check_stdout` flag instructs the autograder to check `stdout` output from the `print` function. 

```python
# print_digits.py
from gapper import problem

@problem(check_stdout=True)
def print_digits(n: int) -> None:
    print(n % 10)
    if n >= 10:
        print_digits(n // 10)
```

Suppose you want to create 10 tests, each worth 1 point. In addition, 4 of them are hand written and others are randomly generated. You can import `test_case` and `test_cases` from `gapper`, and invoke them as you do with the `problem` directive. The following is an example. 


```python
# print_digits.py
from gapper import problem, test_case, test_cases
import random


@test_cases.param_iter(
    ([random.randint(100, 10000)] for _ in range(3)), gap_max_score=1, gap_hidden=True
)
@test_cases.param_iter(
    ([random.randint(100, 10000)] for _ in range(3)), gap_max_score=1
)
@test_case(1, gap_max_score=1)
@test_case(1234, gap_max_score=1)
@test_case(3731, gap_max_score=1)
@test_case(7, gap_max_score=1)
@problem(check_stdout=True)
def print_digits(n: int) -> None:
    print(n % 10)
    if n >= 10:
        print_digits(n // 10)
```

You can then in the command line invoke `gapper gen print_digits.py`, which will generate a `print_digits.zip` file. Note that, the random numbers are generated during creation time instead judging time, meaning once the autograder is created, the random numbers are chosen and fixed for all student submissions. 

On gradescope, when creating a new assignment, choose `Programming Assignment` and fill in the required details. 

<img width="1289" alt="image" src="https://github.com/FlickerSoul/gapper/assets/13360148/b43335fa-c403-447e-b4d1-f4cb18523848">

Then, on the `configure autograder` page, click `Select Autograder (.zip)` button, choose the `print_digits.zip` file from your filesystem, and the click `Update Autograder`.

<img width="873" alt="image" src="https://github.com/FlickerSoul/gapper/assets/13360148/d801bf10-8c62-4d3a-aefc-d99c080846a8">

After the autograder is built, you can click on `Test Autograder` next to the `Update Autograder` button, and upload the `print_digits.py` solution to see the grading result. 

<img width="2180" alt="image" src="https://github.com/FlickerSoul/gapper/assets/13360148/b1c7a82b-6b22-4e80-a6dc-9e50a4c3ca1c">


