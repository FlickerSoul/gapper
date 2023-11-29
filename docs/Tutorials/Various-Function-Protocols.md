# Various Function Protocols

It can be confusing to remember all function protocols used in gapper. Below, we list the function signatures and their docstrings for each use case.

## `gap_override_test`
::: gapper.core.types
    options:
        members: 
            - CustomTestFn
            - CustomTestData

## `gap_override_check`
::: gapper.core.types
    options:
        members: 
            - CustomEqualityCheckFn
            - CustomEqualityTestData

## `gap_pre_hook`
::: gapper.core.types
    options:
        members: 
            - PreHookFn
            - PreHookData

## `gap_post_hook`
::: gapper.core.types
    options:
        members: 
            - PostHookFn
            - PostHookData

## `pre_tests`
::: gapper.core.types
    options:
        members: 
            - PreTestsFn
            - PreTestsData


## `post_tests`
::: gapper.core.types
    options:
        members: 
            - PostTestsFn
            - PostTestsData
