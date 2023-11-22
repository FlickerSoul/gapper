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

## `PostTest`, `pre_tests` and `post_tests` API
::: gapper.core.tester.post_tests
::: gapper.core.tester.pre_tests