# Detailed Usage

We will discuss the detailed usage of `gapper`, including installation, CLI commands, how to create a problem, and how to construct test cases. 

## Installation

The python version required is `>=3.12.0`. 

You can either install from PyPI
```bash
pip install gapper
```

or install from source
```bash
git clone https://github.com/FlickerSoul/gapper.git
pip install -e gapper
```

## Prerequisite 

You need a solution to the assignment for which you'd like to create a autograder, no matter it being a function, or a class. 

If you want a brief of the whole process, please refer to the workflow brief in the [home page](Getting-Started.md). 

## Command Line Interface 

Once `gapper` is installed, you can invoke it through either `gap`, `gapper`, or `gradescope-autograder-packer`. 

/// details | ❯ gapper --help
```text
❯ gapper --help

Usage: gapper [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell.                │
│                                                              [default: None]                                            │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or     │
│                                                              customize the installation.                                │
│                                                              [default: None]                                            │
│ --help                                                       Show this message and exit.                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ check              Check if the problem is defined correctly again the gap_check fields.                                │
│ gen                Generate the autograder for a problem.                                                               │
│ login              Login to Gradescope.                                                                                 │
│ run                Run the autograder on an example submission.                                                         │
│ run-in-prod        Run the autograder in production mode.                                                               │
│ upload                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper check --help
```text
❯ gapper check --help

 Usage: gapper check [OPTIONS] PATH

 Check if the problem is defined correctly again the gap_check fields.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    path      PATH  The path to the problem python file. [default: None] [required]                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --auto-inject  -a            Whether to auto inject the tester file. [default: (dynamic)]                               │
│ --inject       -i      PATH  The path to the tester file to inject. [default: (dynamic)]                                │
│ --verbose      -v            Whether to run in verbose mode.                                                            │
│ --help                       Show this message and exit.                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper gen --help
```text
❯ gapper gen --help

 Usage: gapper gen [OPTIONS] PATH

 Generate the autograder for a problem.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    path      PATH  The path to the problem python file. [default: None] [required]                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --save-path          -s      PATH  The directory to save the generated tester file. [default: (dynamic)]                │
│ --auto-inject        -a            Whether to auto inject the tester file. [default: (dynamic)]                         │
│ --inject             -i      PATH  The path to the tester file to inject. [default: (dynamic)]                          │
│ --confirm-overwrite  -y            Confirm overwrite files.                                                             │
│ --verbose            -v            Whether to run in verbose mode.                                                      │
│ --upload             -u            Whether to upload the autograder.                                                    │
│ --gui                -g            Whether to use the GUI to upload.                                                    │
│ --login-save-path    -l      PATH  The path to save the login info.                                                     │
│                                    [default: /Users/flicker_soul/.config/gapper/gs_account.yaml]                        │
│ --ui-debug           -d            Whether to run in verbose mode.                                                      │
│ --help                             Show this message and exit.                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper login --help
```text
❯ gapper login --help

 Usage: gapper login [OPTIONS]

 Login to Gradescope.

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --confirm-store      -s            Confirm storing your login info.                                                     │
│ --confirm-overwrite  -y            Confirm overwrite files.                                                             │
│ --login-save-path    -l      PATH  The path to save the login info.                                                     │
│                                    [default: /Users/flicker_soul/.config/gapper/gs_account.yaml]                        │
│ --verbose            -v            Whether to run in verbose mode.                                                      │
│ --help                             Show this message and exit.                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper run --help
```text
❯ gapper run --help

 Usage: gapper run [OPTIONS] PATH SUBMISSION

 Run the autograder on an example submission.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    path            PATH  The path to the problem python file. [default: None] [required]                              │
│ *    submission      PATH  The path to the submission file. [default: None] [required]                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --metadata     -m      FILE   The path to the submission metadata file. [default: (dynamic)]                            │
│ --auto-inject  -a             Whether to auto inject the tester file. [default: (dynamic)]                              │
│ --inject       -i      PATH   The path to the tester file to inject. [default: (dynamic)]                               │
│ --verbose      -v             Whether to run in verbose mode.                                                           │
│ --total-score          FLOAT  [default: 20]                                                                             │
│ --help                        Show this message and exit.                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper run-in-prod --help
```text
❯ gapper run-in-prod --help

 Usage: gapper run-in-prod [OPTIONS] [TESTER_PATH] [SUBMISSION_DIR]
                           [METADATA_FILE] [OUTPUT_FILE]

 Run the autograder in production mode.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   tester_path         [TESTER_PATH]     The path to the tester pickle file. [default: /autograder/source/tester.pckl]   │
│   submission_dir      [SUBMISSION_DIR]  The path to the submission directory. [default: /autograder/submission]         │
│   metadata_file       [METADATA_FILE]   The path to the submission metadata file.                                       │
│                                         [default: /autograder/submission_metadata.json]                                 │
│   output_file         [OUTPUT_FILE]     The path to the output file. [default: /autograder/results/results.json]        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --verbose  -v        Whether to run in verbose mode. [default: True]                                                    │
│ --help               Show this message and exit.                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper upload --help
```text
❯ gapper upload --help

 Usage: gapper upload [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ gui      Upload an autograder to Gradescope with GUI.                                                                   │
│ ids      Upload an autograder to Gradescope using the cid and aid.                                                      │
│ url      Upload an autograder to Gradescope using the assignment url.                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper upload gui --help
```text
❯ gapper upload gui --help

 Usage: gapper upload gui [OPTIONS] AUTOGRADER_PATH

 Upload an autograder to Gradescope with GUI.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    autograder_path      PATH  The path to the autograder zip file. [default: None] [required]                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --login-save-path  -l      PATH  The path to save the login info.                                                       │
│                                  [default: /Users/flicker_soul/.config/gapper/gs_account.yaml]                          │
│ --ui-debug         -d            Whether to run in verbose mode.                                                        │
│ --help                           Show this message and exit.                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper upload ids --help
```text
❯ gapper upload ids --help

 Usage: gapper upload ids [OPTIONS] AUTOGRADER_PATH [CID] [AID]

 Upload an autograder to Gradescope using the cid and aid.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    autograder_path      PATH   The path to the autograder zip file. [default: None] [required]                        │
│      cid                  [CID]  The course id. [default: None]                                                         │
│      aid                  [AID]  The assignment id. [default: None]                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --login-save-path  -l      PATH  The path to save the login info.                                                       │
│                                  [default: /Users/flicker_soul/.config/gapper/gs_account.yaml]                          │
│ --ui-debug         -d            Whether to run in verbose mode.                                                        │
│ --help                           Show this message and exit.                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

/// details | ❯ gapper upload url --help
```text
❯ gapper upload url --help

 Usage: gapper upload url [OPTIONS] AUTOGRADER_PATH ASSIGNMENT_URL

 Upload an autograder to Gradescope using the assignment url.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    autograder_path      PATH  The path to the autograder zip file. [default: None] [required]                         │
│ *    assignment_url       TEXT  The url to the autograder. [default: None] [required]                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --login-save-path  -l      PATH  The path to save the login info.                                                       │
│                                  [default: /Users/flicker_soul/.config/gapper/gs_account.yaml]                          │
│ --ui-debug         -d            Whether to run in verbose mode.                                                        │
│ --help                           Show this message and exit.                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
///

## Glossary 

- An `assignment` refers to the assignment issued to students, and is often created as one GradeScope assignment entry. 
- A `solution` refers to the code that solves the assignment. 
- A `problem` refers to the definition of an assignment in the autograder. It can be created with the `@problem` decorator. 
- A `test case` refers to one test entry in the GradeScope assignment entry. It can be created with the `@test_case` decorator.  
- `test cases` refer to a group of `test case`s. They can be created in batch with the `@test_cases` decorator. 

## Create A Problem 

We first import `problem` from `gapper` and apply it as an decorator. Examples are provided at the end of this section. 

```python
from gapper import problem

@problem()
def ...
```

The `problem` has two over loads: 

```python
is_script: bool = False
context: Iterable[str] = ()
easy_context: bool = True
```
and 
```python
check_stdout: Optional[bool] = None
mock_input: Optional[bool] = None
context: Iterable[str] = ()
easy_context: bool = True
```

`is_script` is used to indicate if the assignment is a script, which is something like the following 

```python
i = input("give me a number: ")
print(f"the square of the number is {i ** 2}")
```
Leaving the `is_script` to `False`, the `@problem()` decorator treat decorated entity without extra interpretation. 

`check_stdout` asks the autograder to compare stdout output (e.g. from the `print` function)

`mock_input` feeds test case arguments into `input` call when the submission is run. 

`context` is used to capture variables in submissions. Please see [(Easy) Context](Easy-Context.md) for more details.


### Examples

- Example 1, autograder sees script 
> Problem:
> ```python
> @problem(is_script=True)
> def distance():
>     x1 = float(input("Location x-coordinate? "))
>     y1 = float(input("Location y-coordinate? "))
>     x2 = float(input("Classroom x-coordinate? "))
>     y2 = float(input("Classroom y-coordinate? "))
>     dx = x2-x1
>     dy = y2-y1
>     d = (dx*dx+dy*dy)**0.5
>     print("Distance:")
>     print(d)
> ```
> Submission:
> ```python
> x1 = float(input("Location x-coordinate? "))
> y1 = float(input("Location y-coordinate? "))
> x2 = float(input("Classroom x-coordinate? "))
> y2 = float(input("Classroom y-coordinate? "))
> dx = x2-x1
> dy = y2-y1
> d = (dx*dx+dy*dy)**0.5
> print("Distance:")
> print(d)
> ```
- Example 2, autograder sees a function 
> Problem: 
> ```python
> @problem()
> def coins(cents):
>     q = cents // 25
>     cents = cents % 25
>     d = cents // 10
>     cents = cents % 10
>     n = cents // 5
>     p = cents % 5
>     return q + d + n + p
> ```
> Submission:
> ```python
> def coins(cents):
>     q = cents // 25
>     cents = cents % 25
>     d = cents // 10
>     cents = cents % 10
>     n = cents // 5
>     p = cents % 5
>     return q + d + n + p
> ```
- Example 3, autograder sees a class 
> Problem: 
> ```python
> @problem()
> class LinkedList:
>     ...
> ```
> Submission: 
> ```python
> class LinkedList:
>     ...
> ```

## Create test case(s)

You can import `test_case` and `test_cases` to help the generation of tests. The two helpers are treated as decorators and should be applied after the `@problem()` decorator. For example, 

```python
from gapper import problem, test_case, test_cases, param

@test_cases.param_iter((i, i + 1) for i in range(10))
@test_cases.params([1, 2], param(1, b=1), param(1, b=3))
@test_case(1, b=4)
@problem()
def fn(a, b):
    ...
```

### Specify Parameters 

Given a function `def fn()`, arguments specified in `@test_case()` will be unfolded to parameters of fn when testing. That is, for instance, the input of `a`, `args`, `kw=1`, and `kwargs` in `@test_case(a, *args, kw=1, **kwargs)` will result in `fn(a, *args, kw=1, **kwargs)` when testing. 

When using `@test_cases()` one __has__ to choose a flavor of `test_cases` before proceeding. The options currently are `params`, `param_iter`, `singular_params`, and `singular_param_iter`. To use choose the option, one specify by using `@test_cases.<option>()`. For example, `@test_cases.params()`. Depending on the option, you can usually pass either `Iterable`s or `param`s as arguments to the decorator `@test_cases()`. For example, `@test_cases.params([1, 2], param(3, b=4))`. Note that `param` is the preferred way to define test cases since it is equivalent to `@test_case` semantically. 

The following is the explanation of the effect of each option. 

- `params` takes in __any__ number of `Sequence` or `param`. Each `Sequence` or `param` is equivalent to specifying a `@test_case()`. For example, `@test_cases.params([1, 2], param(1, b=1))` is equivalent to specifying two tests cases, `@test_case(1, 2)` and `@test_case(1, b=1)`. 
- `param_iter` takes in __a__ `Iterable` object of `Sequence` or `param`. `@test_cases.param_iter(iter)` is equivalent to `@test_cases.params(*iter)`. For example, 
  
  ```python
  iter = ([i, i + 1] for i in range(1, 3))
  @test_cases.param_iter(iter)
  def fn(a, b):
    ...
  ...
  ```
  is equivalent to 
  ```python
  @test_cases.params([1, 1 + 1], [2, 2 + 1])
  ```
- `singular_params` is similar to `params` except it does not unfold `Sequence` like `params`. That is, `@test_cases.singular_params([1, 2], param(1, b=1))` is equivalent to specifying two tests cases, `@test_case([1, 2])` and `@test_case(1, b=1)`.
- `singular_param_iter` is similar to `param_iter`. `@test_cases.singular_param_iter(iter)` is equivalent to `@test_cases.singular_params(*iter)`. 

### Specify Test Options

You can configure test cases' properties by using keyword arguments start with `gap_`. For each test case, the supported options are 

```python
gap_expect: The expected output of the test case.
gap_expect_stdout: The expected stdout of the test case.
gap_hidden: Whether the test case is hidden.
gap_name: The name of the test case.
gap_extra_points: The extra credit of the test case.
gap_override_check: The custom equality check function.
gap_override_test: The custom test function.
gap_description: The description of the test case.
gap_is_pipeline: Whether the test case is a pipeline.
gap_max_score: The max score of the test case.
gap_weight: The weight of the test case.
```

We will dedicate a page to discuss their usages. [gap_ Keywords](gap_-Keywords.md)

### Examples

You can notice that the `@test_case` and `@test_cases` decorators take in parameters that should be passed into the function under test. 

```python
from gapper import problem, test_case, test_cases

@test_cases.params([5, 6], [7, 8])  # test_cases is a decorator that takes in a list of test cases
@test_case(3, 4)                    # test_case is a decorator that takes in a single test case
@test_case(1, 2)                    # they together generate 4 tests, where the parameters are 
@problem()                          # x=1,y=2; x=3,y=4; x=5,y=6; x=7,y=8
def add(x: int, y: int) -> int:
    return x + y
```

The following are several ways to specify test cases. 

This is how you can specify a test cases with one iterable parameter.

```python
from gapper import problem, test_cases, param
from typing import Iterable, Generator
import random

def randomly_generate_numbers(times: int) -> Generator[param, None, None]:
    for _ in range(times):
        yield param([random.randint(0, 100) for _ in range(random.randint(0, 100))])

@test_cases.param_iterm(randomly_generate_numbers(10), gap_max_score=1) # the first two lines have the same semantics, which is creating 
@test_cases.params(*randomly_generate_numbers(10), gap_max_score=1)     # 10 random generated numbers, each worth 1 point 
@test_cases.params(param([1, 2]), param([3, 4], gap_max_score=2))       # `param` is a helper that allows you to specify parameters, in a more 
@test_cases.params([[5, 6]], [[7, 8]], gap_hidden=[True, False])        # readable way. This problem has 6 test cases, where the parameters 
@problem()                                                              # are [1,2]; [3,4]; [5,6]; [7,8]. The three ways of specifying 
def sum_many(args: Iterable[int]) -> int:                               # parameters are equivalent. Note that @test_cases.params([5, 6], [7, 8])  
    return sum(args)                                                    # doesn't work because will treat [x, y] as two parameters instead of a list.
```

This is how you can specify a test cases with keyword arguments.

```python
from gapper import problem, test_cases, test_case, param

@test_cases(param(0, x = 1, y = 2), param(3, x = 4, y = 5))  # You can also specify kwargs in the param or test_case 
@test_case(6, x = 7, y = 8)                                  # decorator. Note that using param is the only way to 
@test_case(9, x = 10)                                        # specify kwargs in test_cases.
@problem()                                                   
def add(a: int, x: int, y: int = 20) -> int:
    return a * x + y
```

This is how you can override the equality check between the solution and the submission.

```python
from gapper import problem, test_cases, test_case  
from typing import Iterable

def override_check(solution_ans, submission_ans) -> bool:
    return set(solution_ans) == set(submission_ans)

@test_cases(11, 12, 13, gap_override_check=override_check)
@test_case(10, gap_override_check=override_check)
@problem()
def generate_numbers(x: int) -> Iterable[int]:
    return range(x)
```

This is how you can override how the submission should be tested.

```python
from gapper import problem, test_case, test_cases
from gapper.core.unittest_wrapper import TestCaseWrapper
from gapper.core.test_result import TestResult


def override_test(tc: TestCaseWrapper, result: TestResult, solution, submission):
    solution_answer = solution(*tc.test_param.args)
    student_answer = submission(*tc.test_param.args)
    tc.assertEqual(solution_answer, student_answer)

    result.set_pass_status("failed")


@test_cases([3, 4], [5, 6], gap_override_test=override_test)
@test_case(1, 2, gap_override_test=override_test)
@problem()
def add(x: int, y: int) -> int:
    if x < 0 or y < 0:
        raise ValueError("x and y must be positive")
    return x + y
```






