# `Tester`, `pre_tests` and `post_tests`

## Note 

`post_tests` is an alias of `PostTest` and `pre_tests` is an alias of `PreTest`. That is

```python
from gapper import post_tests, pre_tests
from gapper.core.tester import PostTests, PreTests

assert post_tests is PostTests
assert pre_tests is PreTests
```

## Tester API
::: gapper.core.tester.tester_def

## `PreTests`, `pre_tests`, `PostTests`, and `post_tests` API

### `PreTests` and `pre_tests`
::: gapper.core.tester
    options:
        members:
            - pre_tests
            - PreTests  
            - post_tests
            - PostTests 
