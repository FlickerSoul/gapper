# @test_case(s) -- `TestParam` and `TestParamBundle`,  and `gap_*_hooks`

## Note

`test_case` and `param` are aliases of `TestParam`, and `test_cases` is a alias of `TestParamBundle` respectively.

```python
from gapper import test_case, param
from gapper.core.test_parameter import TestParam

assert param is TestParam
assert test_case is TestParam
```

```python
from gapper import test_cases
from gapper.core.test_parameter import TestParamBundle

assert test_cases is TestParamBundle
```

## `test_case(s)` API
::: gapper.core.test_parameter

## `gap_*_hooks` API
::: gapper.core.unittest_wrapper.wrapper_hooks
    options:
        members:
            - PreHook
            - pre_hook
            - PostHook  
            - post_hook 