from __future__ import annotations

import abc
import typing as t

from typing_extensions import Never

from _fp._result_types import L, R, T

from .result import Err, Ok

S = t.TypeVar("S")
E = t.TypeVar("E")


WResult: t.TypeAlias = "WOk[L, R, T] | WErr[L, R, T]"


class WResultABC(t.Generic[L, R, T], metaclass=abc.ABCMeta):
    value: L | R
    entries: tuple[T, ...]

    @abc.abstractmethod  # pragma: no mutate
    def __bool__(self) -> bool:
        """Return True if the writer result is a `WOk` instance, False otherwise."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def __eq__(self, other: object) -> bool:
        """Return True if other writer result is equal to this result, False otherwise."""

    @abc.abstractmethod  # pragma: no mutate
    def __hash__(self) -> int:
        """Return unique hash for the writer result (used when working with set objects
        and dict keys for example)."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def __repr__(self) -> str:
        """Human readable representation of the writer result."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def map(self, fn: t.Callable[[L], S]) -> WResult[S, R, T]:
        """Apply a function to the value contained in an `WOk` instance.

        ### When to use ?

        * You want to transform a success value, while preserving the error type,
        and the extra data type.

        ### When to NOT use ?

        * You want to transform a success value using a function which returns a
          `WResult` object. In this case use `bind()` instead.

        ### Examples

        - `Ok` instances are transformed:

        >>> assert WOk(1, "hello").map(lambda x: x + 1) == WOk(2, "hello")

        - `Err` instances are forwarded:

        >>> assert WErr(1, "BOOM").map(lambda x: x + 1) == WErr(1, "BOOM")
        """
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def map_err(self, fn: t.Callable[[R], E]) -> WResult[L, E, T]:
        """Apply a function to the value contained in a `WErr` instance
        or forward `Ok` instance."""
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def bind(self, fn: t.Callable[[L], WResult[S, R, T]]) -> WResult[S, R, T]:
        """Apply a function returning a result to the value contained in
        an `WOk` instance or forward `WErr` instance.

        ### When to use ?

        * You want to convert from success type to error type or to another
          success type.
          Checkout "Railway oriented programming" for more details
           (https://fsharpforfunandprofit.com/rop/#slides).

        * You want to change BOTH success type and error type. This is NOT possible
          directly, but can be achieved by using first `bind_err()` to change error
          type, and then `bind()` to change success type.

        ### When NOT to use ?

        * You want to transform a success using a function which returns a value. In this case, use `map()` instead.
        * You want the function being bound to always return an error value. In this
          case use `fail()` instead.

        ### Examples

        - `WOk` instances are transformed:

        >>> assert WOk(1, "once").bind(lambda x: WOk(x + 1, "twice")) == WOk(2, "once", "twice")
        >>> assert WOk(1, "once").bind(lambda x: WErr("oh no", "twice")) == WErr("oh no", "once", "twice")

        - `WErr` instances are forwarded:

        >>> assert WErr(1).bind(lambda x: WOk(x + 1)) == WErr(1)
        >>> assert WErr(1, "BOOM").bind(lambda x: WErr(x, "oh no")) == WErr(1, "BOOM")
        """
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def bind_err(self, fn: t.Callable[[R], WResult[L, E, T]]) -> WResult[L, E, T]:
        """Apply a function returning a result to the value contained in
        an `Err` instance or forward `Ok` instance."""
        raise NotImplementedError


class WOk(WResultABC[L, R, T]):
    """Writer monad class for Ok values."""

    value: L

    def __init__(self, value: L, *entries: T):
        self.entries = tuple(entries)
        self.value = value

    def __bool__(self) -> t.Literal[True]:
        return True

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and (other.value == self.value)
            and (other.entries == self.entries)
        )

    def __hash__(self) -> int:
        return hash(("WOk", self.value, tuple(self.entries)))

    def __repr__(self) -> str:
        return f"WOk({repr(self.value)})"

    def unpack(self) -> tuple[Ok[L, R], tuple[T, ...]]:
        return (Ok(self.value), self.entries)

    def map(self, fn: t.Callable[[L], S]) -> WOk[S, R, T]:
        return WOk(fn(self.value), *self.entries)

    def map_err(self, fn: t.Callable[[R], E]) -> WOk[L, E, T]:
        return self  # type: ignore

    def bind(self, fn: t.Callable[[L], WResult[S, R, T]]) -> WResult[S, R, T]:
        res = fn(self.value)
        if res:
            return WOk(res.value, *self.entries, *res.entries)
        return WErr(res.value, *self.entries, *res.entries)

    def bind_err(self, fn: t.Callable[[R], WResult[L, E, T]]) -> WOk[L, E, T]:
        return self  # type: ignore

    def rescue(self, fn: t.Callable[[R], L]) -> WOk[L, Never, T]:
        return self  # type: ignore

    def fail(self, fn: t.Callable[[L], R]) -> WErr[Never, R, T]:
        return WErr(fn(self.value), *self.entries)

    def flush(self, fn: t.Callable[[tuple[T, ...]], None]) -> Ok[L, R]:
        fn(self.entries)
        return Ok(self.value)


class WErr(WResultABC[L, R, T]):
    """Writer monad class for Err values."""

    value: R

    def __init__(self, value: R, *entries: T):
        self.entries = tuple(entries)
        self.value = value

    def __bool__(self) -> t.Literal[False]:
        return False

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and (other.value == self.value)
            and (other.entries == self.entries)
        )

    def __hash__(self) -> int:
        return hash(("WErr", self.value, tuple(self.entries)))

    def __repr__(self) -> str:
        return f"WErr({repr(self.value)})"

    def unpack(self) -> tuple[Err[L, R], tuple[T, ...]]:
        return (Err(self.value), self.entries)

    def map(self, fn: t.Callable[[L], S]) -> WErr[S, R, T]:
        return self  # type: ignore

    def map_err(self, fn: t.Callable[[R], E]) -> WErr[L, E, T]:
        return WErr(fn(self.value), *self.entries)

    def bind(self, fn: t.Callable[[L], WResult[S, R, T]]) -> WErr[S, R, T]:
        return self  # type: ignore

    def bind_err(self, fn: t.Callable[[R], WResult[L, E, T]]) -> WResult[L, E, T]:
        res = fn(self.value)
        if not res:
            return WErr(res.value, *self.entries, *res.entries)
        return WOk(res.value, *self.entries, *res.entries)

    def rescue(self, fn: t.Callable[[R], L]) -> WOk[L, Never, T]:
        return WOk(fn(self.value), *self.entries)

    def fail(self, fn: t.Callable[[L], R]) -> WErr[Never, R, T]:
        return self  # type: ignore

    def flush(self, fn: t.Callable[[tuple[T, ...]], None]) -> Err[L, R]:
        fn(self.entries)
        return Err(self.value)
