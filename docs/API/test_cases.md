# @test_case(s) -- `TestParam` and `TestParamBundle`

Note that 

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

::: gapper.core.test_parameter