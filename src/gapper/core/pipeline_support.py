"""Support for pipeline actions."""
from __future__ import annotations

from typing import Any, ClassVar, Type

__all__ = [
    "PipelineBase",
    "PipelineFactory",
    "Constructor",
    "Function",
    "Property",
]


class PipelineBase:
    """A pipeline action base class. All pipeline actions should inherit from this class."""

    def __init__(
        self, name: str, *args, _pipeline_replace: bool = False, **kwargs
    ) -> None:
        """A pipeline base class.

        :param name: The name of the attribute to be extracted from the piped object.
        :param _pipeline_replace: Whether to replace the piped object with the result of the pipeline.
        :param args: The arguments to pass to the attribute.
        """
        self._replace = _pipeline_replace
        self._name = name
        self._args = args
        self._kwargs = kwargs

    @property
    def replace(self) -> bool:
        """Whether to replace the piped object with the result of the pipeline action."""
        return self._replace

    def __call__(self, obj: Any) -> Any:
        """Call the pipeline action on the object."""
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._name!r}, {self._args!r}, {self._kwargs!r})"


class PipelineFactory:
    """A pipeline action factory base class. All pipeline action factories should inherit from this class.

    The semantics of a pipeline action factory is to generate a pipeline action when called. That is

        pipeline_factory = PipelineFactory(name)
        pipeline_action = pipeline_factory(*args, **kwargs)

        @test_case(
          pipeline_action,
          pipeline_factory(*args, **kwargs),
        )
        ...

    :cvar ValueType: The type of the pipeline action generated by the factory.
    """

    ValueType: ClassVar[Type[PipelineBase]]

    def __init__(self, name: str, *, _pipeline_replace: bool = False) -> None:
        self._replace = _pipeline_replace
        self._name = name

    def __call__(self, *args: Any, **kwargs: Any) -> ValueType:  # noqa: F821
        return type(self).ValueType(
            self._name, *args, _pipeline_replace=self._replace, **kwargs
        )


class Constructor(PipelineFactory):
    """A pipeline action factory generating __init__ calls."""

    class ConstructorEntry(PipelineBase):
        def __call__(self, obj: Type) -> Any:
            return obj(*self._args, **self._kwargs)

    ValueType = ConstructorEntry

    def __init__(self) -> None:
        super().__init__("__init__", _pipeline_replace=True)


class Function(PipelineFactory):
    """A pipeline action factory generating function calls."""

    class FunctionEntry(PipelineBase):
        def __call__(self, obj: Any) -> Any:
            """Call the function on the object."""
            caller = getattr(obj, self._name, None)
            if caller is None:
                raise AttributeError(f"Object {obj} has no attribute {self._name}.")
            return caller(*self._args, **self._kwargs)

    ValueType = FunctionEntry


class Property(PipelineBase):
    """A pipeline action factory generating property lookups."""

    def __init__(self, name: str) -> None:
        """Init the pipeline action."""
        super().__init__(name)

    def __call__(self, obj: Any) -> None:
        """Get Property from object."""
        return getattr(obj, self._name)
