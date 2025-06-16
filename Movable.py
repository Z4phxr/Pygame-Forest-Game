from typing import runtime_checkable, Protocol, Any


@runtime_checkable
class Movable(Protocol):
    """
    Protocol for objects that support a .move(...) method.
    Use isinstance(obj, Movable) to check at runtime.
    """
    def move(self, *args: Any, **kwargs: Any) -> None:
        pass