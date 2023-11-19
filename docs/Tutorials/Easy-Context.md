# (Easy) Context

Sometimes, you might want to capture some definitions in students' submissions for testing purposes. For example, suppose student writes a class `Car` that uses their definition of `GasStation`. You might want to reference the `GasStation` class when overriding tests. 

Note that you can access captured context only in the `gap_override_test` and any tests' pre hooks or post hooks. 

TODO: Finish explanation and add examples.