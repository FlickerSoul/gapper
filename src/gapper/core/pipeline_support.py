from __future__ import annotations

from typing import Any, ClassVar, Type


class PipelineBase:
    def __init__(
        self, name: str, *args, _pipeline_replace: bool = False, **kwargs
    ) -> None:
        self._replace = _pipeline_replace
        self._name = name
        self._args = args
        self._kwargs = kwargs

    @property
    def replace(self) -> bool:
        return self._replace

    def __call__(self, obj: Any) -> Any:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._name!r}, {self._args!r}, {self._kwargs!r})"


class PipelineFactory:
    ValueType: ClassVar[Type[PipelineBase]]

    def __init__(self, name: str, *, _pipeline_replace: bool = False) -> None:
        self._replace = _pipeline_replace
        self._name = name

    def __call__(self, *args: Any, **kwargs: Any) -> ValueType:
        return type(self).ValueType(
            self._name, *args, _pipeline_replace=self._replace, **kwargs
        )


class Constructor(PipelineFactory):
    class ConstructorEntry(PipelineBase):
        def __call__(self, obj: Type) -> Any:
            return obj(*self._args, **self._kwargs)

    ValueType = ConstructorEntry

    def __init__(self) -> None:
        super().__init__("__init__", _pipeline_replace=True)


class Function(PipelineFactory):
    class FunctionEntry(PipelineBase):
        def __call__(self, obj: Any) -> Any:
            caller = getattr(obj, self._name, None)
            if caller is None:
                raise AttributeError(f"Object {obj} has no attribute {self._name}.")
            return caller(*self._args, **self._kwargs)

    ValueType = FunctionEntry


class Property(PipelineBase):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __call__(self, obj: Any) -> None:
        return getattr(obj, self._name)
