from __future__ import annotations

import abc
import typing as t

from typing_extensions import Never

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

    @abc.abstractmethod  # pragma: no mutate
    def __bool__(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def __hash__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def map(self, fn: t.Callable[[L], T]) -> Result[T, R]:
        """Apply a function to the value contained in an `Ok` instance.

        ### When to use ?

        * You want to transform a success value, while preserving the error type.

        ### When to NOT use ?

        * You want to transform a success value using a function which returns a
          `Result` object. In this case use `bind()` instead.

        ### Examples

        - `Ok` instances are transformed:

        >>> assert Ok(1).map(lambda x: x + 1) == Ok(2)

        - `Err` instances are forwarded:

        >>> assert Err(1).map(lambda x: x + 1) == Err(1)
        """
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def map_err(self, fn: t.Callable[[R], T]) -> Result[L, T]:
        """Apply a function to the value contained in an `Err` instance.

        ### When to use ?

        * You want to transform an error value, while preserving the success type.

        ### When NOT to use ?

        * You want to transform an error value with a function which returns a
          `Result` object. In this case, use `bind_err()` instead

        ### Examples

        - `Err` instances are transformed:

        >>> assert Err(1).map_err(lambda x: x + 1) == Err(2)

        - `Ok` instances are forwarded:

        >>> assert Ok(1).map_err(lambda x: x + 1) == Ok(1)
        """
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def bind(self, fn: t.Callable[[L], Result[T, R]]) -> Result[T, R]:
        """Apply a function returning a result to the value contained in
        an `Ok` instance or forward `Err` instance.

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

        - `Ok` instances are transformed:

        >>> assert Ok(1).bind(lambda x: Ok(x + 1)) == Ok(2)
        >>> assert Ok(1).bind(lambda x: Err("oh no")) == Err("oh no")

        - `Err` instances are forwarded:

        >>> assert Err(1).bind(lambda x: Ok(x + 1)) == Err(1)
        >>> assert Err("BOOM").bind(lambda x: Err("oh no")) == Err("BOOM")
        """
        raise NotImplementedError

    @abc.abstractmethod  # pragma: no mutate
    def bind_err(self, fn: t.Callable[[R], Result[L, T]]) -> Result[L, T]:
        """Apply a function returning a result to the value contained in
        an `Err` instance or forward `Ok` instance.

        ### When to use ?

        * You want to convert from one error type to a success or to another
          error type.
          Checkout "Railway oriented programming" for more details
           (https://fsharpforfunandprofit.com/rop/#slides).

        * You want to change BOTH success type and error type. This is NOT possible
          directly, but can be achieved by using first `bind_err()` to change error
          type, and then `bind()` to change success type.

        ### When NOT to use ?

        * You want to transform an error using a function returning a value. In this case, use `map_err()` instead.
        * You want the function being bound to awlays return an `Ok` result. In this
          case use `rescue()` instead.

        ### Examples

        - `Err` instances are transformed:

        >>> assert Err(1).bind_err(lambda x: Err(x + 1)) == Err(2)
        >>> assert Err(1).bind_err(lambda x: Ok("yes")) == Ok("yes")

        - `Ok` instances are forwarded:

        >>> assert Ok(1).bind_err(lambda x: Ok(x + 1)) == Ok(1)
        >>> assert Ok("yes").bind_err(lambda x: Err("no")) == Ok("yes")
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rescue(self, fn: t.Callable[[R], L]) -> Result[L, Never]:
        """Transform an `Err` value into an `Ok` value and annotate result as always successful.

        Once `rescue()` is called, it's possible to use `.unwrap()` to get the value.

        ### When to use ?

        * You want to make sure all errors are processed at some point, for example:
        You're calling a usecase from an HTTP controller, and you want to get
        an HTTP response for both error and responses. After calling the usecase,
        you can use `map()` to convert a success into another success holding an
        HTTP response, and use `rescue()` to convert an error into a
        success holding an HTTP response (e.g, create a 5XX or 4XX HTTP error response).

        ### Examples

        - `Err` values are transformed:

        >>> assert Err(1).rescue(lambda x: 0) == Ok[int, Never](0)

        - `Ok` values are forwarded:

        >>> assert Ok(1).rescue(lambda x: 0) == Ok[int, Never](1)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fail(self, fn: t.Callable[[L], R]) -> Result[Never, R]:
        """Transform an Ok value into an Err value and annotate result as always failed.

        ### When to use ?

        * You're performing an action which is normally expected to succeed, but you
        want it to fail for a specific reason.
        For example, in order to verify that a key does not exist, you may use
        a `find_key()` function which returns a `Result[str, KeyValueError]` object.
        In such case, you can use `fail()` to convert a success (when key is found)
        into an error.

        ### Examples

        * `Ok` instances are transformed:

        >>> assert Ok(1).fail(lambda x: "oh no") == Err("oh no")

        * `Err` instances are forwarded:

        >>> assert Err("BOOM").fail(lambda x: "oh no") == Err("BOOM")
        """
        raise NotImplementedError

    def unwrap(self: ResultABC[L, Never]) -> L:
        """Get the success value out of an `Ok` result.

        ### When to use ?

        * You previously used `rescue` to guarantee that all errors have been
        handled, and you want to transform the contained value. For example,
        you called a usecase within an HTTP controller, and used `map()` to
        transform success into an HTTP response, as well as `rescue()` to
        transform error into an HTTP response. At this point, it is safe
        to call `.unwrap()` to get the HTTP response object.

        ### When NOT to use ?

        * You did not call `rescue()` previously. Type checkers (mypy, pyright)
          will detect an error in such cases and at runtime, a `RuntimeError` will
          be raised.
        * You still want to chain functions, in this case, use `map()` or `bind()`
          instead.

        ### Examples

        * Make sure errors are transformed into success by calling `rescue()` first:

        >>> assert Err("oh no").rescue(lambda x: 0).unwrap() == 0
        """
        return self.value


class Ok(ResultABC[L, R]):
    value: L
    """The value contained in an `Ok` instance."""

    def __init__(self, value: L) -> None:
        """Create an `Ok` instance with a value."""
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and (self.value == other.value)

    def __hash__(self) -> int:
        return hash(("Ok", self.value))

    def __repr__(self) -> str:
        return f"Ok({repr(self.value)})"

    def __bool__(self) -> t.Literal[True]:
        return True

    def map(self, fn: t.Callable[[L], T]) -> Ok[T, R]:
        return Ok(fn(self.value))

    def map_err(self, fn: t.Callable[[R], T]) -> Ok[L, T]:
        return self  # type: ignore[return-value]

    def bind(self, fn: t.Callable[[L], Result[T, R]]) -> Result[T, R]:
        return fn(self.value)

    def bind_err(self, fn: t.Callable[[R], Result[L, T]]) -> Ok[L, T]:
        return self  # type: ignore[return-value]

    def rescue(self, fn: t.Callable[[R], L]) -> Ok[L, Never]:
        return self  # type: ignore[return-value]

    def fail(self, fn: t.Callable[[L], R]) -> Err[Never, R]:
        return Err(fn(self.value))


class Err(ResultABC[L, R]):
    value: R
    """The value contained in an `Err` instance."""

    def __init__(self, value: R) -> None:
        """Create an `Err` instance with a value."""
        self.value = value

    def __bool__(self) -> t.Literal[False]:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and (self.value == other.value)

    def __hash__(self) -> int:
        return hash(("Err", self.value))

    def __repr__(self) -> str:
        return f"Err({repr(self.value)})"

    def map(self, fn: t.Callable[[L], T]) -> Err[T, R]:
        return self  # type: ignore[return-value]

    def map_err(self, fn: t.Callable[[R], T]) -> Err[L, T]:
        return Err(fn(self.value))

    def bind(self, fn: t.Callable[[L], Result[T, R]]) -> Err[T, R]:
        return self  # type: ignore[return-value]

    def bind_err(self, fn: t.Callable[[R], Result[L, T]]) -> Result[L, T]:
        return fn(self.value)

    def rescue(self, fn: t.Callable[[R], L]) -> Ok[L, Never]:
        return Ok(fn(self.value))

    def fail(self, fn: t.Callable[[L], R]) -> Err[Never, R]:
        return self  # type: ignore[return-value]
