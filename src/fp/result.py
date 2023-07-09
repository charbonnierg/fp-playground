from __future__ import annotations

import abc
import typing as t

from _fp._result_types import L, R, T

Result: t.TypeAlias = "Ok[L, R] | Err[L, R]"  # pragma: no mutate
"""Type alias for a Result type.

Result is a union type of `Ok[L, R]` and `Err[L, R]`,

where `L` is the type of the value contained in an `Ok` instance,
and `R` is the type of the value contained in an `Err` instance.

Both `Ok` and `Err` requires two type arguments, `L` and `R`,
because they are covariant in `L` and `R`
"""


class ResultABC(t.Generic[L, R], metaclass=abc.ABCMeta):
    value: L | R

    def __eq__(self, other: object) -> bool:
        """Compare two Result instances.

        Two result instances are equal when they are both `Ok` or
        `Err` instances, and their values are equal.
        """
        return isinstance(other, self.__class__) and (self.value == other.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.value)})"

    @abc.abstractmethod  # pragma: no mutate
    def __bool__(self) -> bool:
        """Return True if the result is an `Ok` instance, False otherwise."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def map(self, fn: t.Callable[[L], T]) -> Result[T, R]:
        """Apply a function to the value contained in an `Ok` instance
        or forward `Err` instance."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def map_err(self, fn: t.Callable[[R], T]) -> Result[L, T]:
        """Apply a function to the value contained in an `Err` instance
        or forward `Ok` instance."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def bind(self, fn: t.Callable[[L], Result[T, R]]) -> Result[T, R]:
        """Apply a function returning a result to the value contained in
        an `Ok` instance or forward `Err` instance."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def bind_err(self, fn: t.Callable[[R], Result[L, T]]) -> Result[L, T]:
        """Apply a function returning a result to the value contained in
        an `Err` instance or forward `Ok` instance."""
        raise NotImplementedError


class Ok(ResultABC[L, R]):
    value: L
    """The value contained in an `Ok` instance."""

    def __init__(self, value: L) -> None:
        """Create an `Ok` instance with a value."""
        self.value = value

    def __bool__(self) -> t.Literal[True]:
        """Always return True."""
        return True

    def map(self, fn: t.Callable[[L], T]) -> Result[T, R]:
        """Apply a function to the value contained in an `Ok` instance."""
        return Ok(fn(self.value))

    def map_err(self, fn: t.Callable[[R], T]) -> Result[L, T]:
        """Forward `Ok` instance."""
        return self  # type: ignore[return-value]

    def bind(self, fn: t.Callable[[L], Result[T, R]]) -> Result[T, R]:
        """Apply a function returning a result to the value contained in
        an `Ok` instance."""
        return fn(self.value)

    def bind_err(self, fn: t.Callable[[R], Result[L, T]]) -> Result[L, T]:
        """Forward `Ok` instance."""
        return self  # type: ignore[return-value]


class Err(ResultABC[L, R]):
    value: R
    """The value contained in an `Err` instance."""

    def __init__(self, value: R) -> None:
        """Create an `Err` instance with a value."""
        self.value = value

    def __bool__(self) -> t.Literal[False]:
        """Always return False."""
        return False

    def map(self, fn: t.Callable[[L], T]) -> Result[T, R]:
        """Forward `Err` instance."""
        return self  # type: ignore[return-value]

    def map_err(self, fn: t.Callable[[R], T]) -> Result[L, T]:
        """Apply a function to the value contained in an `Err` instance."""
        return Err(fn(self.value))

    def bind(self, fn: t.Callable[[L], Result[T, R]]) -> Result[T, R]:
        """Forward `Err` instance."""
        return self  # type: ignore[return-value]

    def bind_err(self, fn: t.Callable[[R], Result[L, T]]) -> Result[L, T]:
        """Apply a function returning a result to the value contained in
        an `Err` instance."""
        return fn(self.value)
