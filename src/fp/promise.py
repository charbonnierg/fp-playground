from __future__ import annotations

import asyncio  # type: ignore  # noqa: F401
import typing as t
from asyncio import sleep  # type: ignore  # noqa: F401
from inspect import iscoroutinefunction
from types import AsyncGeneratorType

from _fp._result_types import E, L, R, S, T

from .result import Err, Ok, Result
from .writer import WErr, WOk, WResult


def head(generator: t.AsyncGenerator[T, t.Any]) -> t.Callable[..., t.Awaitable[T]]:
    return generator.__anext__


class Promise(t.Generic[L, R]):
    """A promise of a Result which will be returned by a coroutine function or an awaitable.

    A Promise is a generic type of `L` and `R`, where `Result[L, R]` is the result type
    of the coroutine function or the awaitable it wraps.
    """

    _coro: t.Awaitable[Result[L, R]]

    def __init__(
        self, coro: t.Awaitable[Result[L, R]] | t.AsyncGenerator[Result[L, R], None]
    ):
        """Create a new `Promise` out of a coroutine function."""
        if isinstance(coro, AsyncGeneratorType):
            self._coro = coro.__anext__()
        else:
            self._coro = coro  # type: ignore

    def __await__(self) -> t.Generator[t.Any, None, Result[L, R]]:
        return self._coro.__await__()

    async def wait(self) -> Result[L, R]:
        """Wait for the promise to complete."""
        return await self

    @classmethod
    def ok_from(
        cls, coro: t.Awaitable[L] | t.AsyncGenerator[L, t.Any]
    ) -> Promise[L, R]:
        """Create a promise of an `Ok` value from a coroutine function or an awaitable.

        >>> assert asyncio.run(
        ...     Promise.ok_from(sleep(0, result=1)).wait()
        ... ) == Ok(1)
        """

        async def _from_ok() -> Result[L, R]:
            if isinstance(coro, AsyncGeneratorType):
                return Ok(await coro.__anext__())
            return Ok(await coro)  # type: ignore

        return Promise(_from_ok())

    @classmethod
    def err_from(
        cls, coro: t.Awaitable[R] | t.AsyncGenerator[R, t.Any]
    ) -> Promise[L, R]:
        """Create a promise of an `Err` value from a coroutine function or an awaitable.

        >>> assert asyncio.run(
        ...     Promise.err_from(sleep(0, result=1)).wait()
        ... ) == Err(1)
        """

        async def _err_from() -> Result[L, R]:
            if isinstance(coro, AsyncGeneratorType):
                return Err(await coro.__anext__())
            return Err(await coro)  # type: ignore

        return Promise(_err_from())

    def map(
        self,
        fn: t.Callable[[L], T] | t.Callable[[L], t.Awaitable[T]],
    ) -> Promise[T, R]:
        """Apply a function to the value contained in `Ok` promise result,
        or forward `Err` promise result. It's possible to map both
        synchronous and asynchronous functions.

        >>> assert asyncio.run(
        ...     Promise.ok_from(sleep(0, result=1))
        ...     .map(lambda x: x+1)
        ...     .wait()
        ... ) == Ok(2)
        """

        async def _map() -> Result[T, R]:
            result = await self._coro
            if not result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                return Ok(await fn(result.value))
            return Ok(fn(result.value))  # type: ignore[arg-type]

        return Promise(_map())

    def map_err(
        self,
        fn: t.Callable[[R], T] | t.Callable[[R], t.Awaitable[T]],
    ) -> Promise[L, T]:
        """Apply a function to the value contained in `Err` promise result,
        or forward `Ok` promise result."""

        async def _map_err() -> Result[L, T]:
            result = await self._coro
            if result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                return Err(await fn(result.value))
            return Err(fn(result.value))  # type: ignore[arg-type]

        return Promise(_map_err())

    def bind(
        self,
        fn: t.Callable[[L], Result[T, R]] | t.Callable[[L], t.Awaitable[Result[T, R]]],
    ) -> Promise[T, R]:
        """Apply a function which must return a result to the value
        contained in `Ok` promise result, or forward `Err` promise result."""

        async def _bind() -> Result[T, R]:
            result = await self._coro
            if not result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                return await fn(result.value)
            return fn(result.value)  # type: ignore[arg-type]

        return Promise(_bind())

    def bind_err(
        self,
        fn: t.Callable[[R], Result[L, T]] | t.Callable[[R], t.Awaitable[Result[L, T]]],
    ) -> Promise[L, T]:
        """Apply a function which must return a result to the value
        contained in `Err` promise result, or forward `Ok` promise result."""

        async def _bind_err() -> Result[L, T]:
            result = await self._coro
            if result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                return await fn(result.value)
            return fn(result.value)  # type: ignore[arg-type]

        return Promise(_bind_err())


class WPromise(t.Generic[L, R, T]):
    """A promise of a WResult (Writer Result) which will be returned by a coroutine function
    or an awaitable.

    A WPromise is a generic type of `L`, `R` and `T`, where `Result[L, R]` is the result type
    of the coroutine function or the awaitable it wraps, and `T` is the type of data
    appended to the writer.
    """

    _coro: t.Awaitable[WResult[L, R, T]]

    def __init__(self, coro: t.Awaitable[WResult[L, R, T]]):
        self._coro = coro

    def __await__(self) -> t.Generator[t.Any, None, WResult[L, R, T]]:
        """Await the coroutine wrapped by the promise and return a writer result."""
        return self._coro.__await__()

    async def wait(self) -> WResult[L, R, T]:
        """Wait for the writer promise to complete."""
        return await self

    @classmethod
    def ok_from(
        cls, coro: t.Awaitable[L] | t.AsyncGenerator[L, t.Any]
    ) -> WPromise[L, R, T]:
        """Create a promise of an `Ok` value from a coroutine function or an awaitable.

        >>> assert asyncio.run(
        ...     WPromise.ok_from(sleep(0, result=1)).wait()
        ... ) == WOk(1)
        """

        async def _from_ok() -> WResult[L, R, T]:
            if isinstance(coro, AsyncGeneratorType):
                return WOk(await coro.__anext__())
            return WOk(await coro)  # type: ignore

        return WPromise(_from_ok())

    @classmethod
    def err_from(
        cls, coro: t.Awaitable[R] | t.AsyncGenerator[R, t.Any]
    ) -> WPromise[L, R, T]:
        """Create a writer promise of an `Err` value from a coroutine function or an awaitable.

        >>> assert asyncio.run(
        ...     WPromise.err_from(sleep(0, result=1)).wait()
        ... ) == WErr(1)
        """

        async def _err_from() -> WResult[L, R, T]:
            if isinstance(coro, AsyncGeneratorType):
                return WErr(await coro.__anext__())
            return WErr(await coro)  # type: ignore

        return WPromise(_err_from())

    def map(
        self,
        fn: t.Callable[[L], S] | t.Callable[[L], t.Awaitable[S]],
    ) -> WPromise[S, R, T]:
        """Apply a function to the value contained in `Ok` promise result,
        or forward `Err` promise result."""

        async def _map() -> WResult[S, R, T]:
            result = await self._coro
            if not result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                return WOk(await fn(result.value), result.entries)  # type: ignore[arg-type]
            return WOk(fn(result.value), result.entries)  # type: ignore[arg-type]

        return WPromise(_map())

    def map_err(
        self,
        fn: t.Callable[[R], E] | t.Callable[[R], t.Awaitable[E]],
    ) -> WPromise[L, E, T]:
        """Apply a function to the value contained in `Err` promise result,
        or forward `Ok` promise result."""

        async def _map_err() -> WResult[L, E, T]:
            result = await self._coro
            if result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                return WErr(await fn(result.value), result.entries)  # type: ignore[arg-type]
            return WErr(fn(result.value), result.entries)  # type: ignore[arg-type]

        return WPromise(_map_err())

    def bind(
        self,
        fn: t.Callable[[L], WResult[S, R, T]]
        | t.Callable[[L], t.Awaitable[WResult[S, R, T]]],
    ) -> WPromise[S, R, T]:
        """Apply a function which must return a result to the value
        contained in `Ok` promise result, or forward `Err` promise result."""

        async def _bind() -> WResult[S, R, T]:
            result = await self._coro
            if not result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                inner_result = await fn(result.value)
            else:
                inner_result = fn(result.value)
            if inner_result:
                return WOk(inner_result.value, result.entries + inner_result.entries)  # type: ignore
            else:
                return WErr(inner_result.value, result.entries + inner_result.entries)  # type: ignore

        return WPromise(_bind())

    def bind_err(
        self,
        fn: t.Callable[[R], WResult[L, E, T]]
        | t.Callable[[R], t.Awaitable[WResult[L, E, T]]],
    ) -> WPromise[L, E, T]:
        """Apply a function which must return a result to the value
        contained in `Err` promise result, or forward `Ok` promise result."""

        async def _bind_err() -> WResult[L, E, T]:
            result = await self._coro
            if result:
                return result  # type: ignore[return-value]
            if iscoroutinefunction(fn):
                inner_result = await fn(result.value)
            else:
                inner_result = fn(result.value)
            if inner_result:
                return WOk(inner_result.value, result.entries + inner_result.entries)  # type: ignore
            else:
                return WErr(inner_result.value, result.entries + inner_result.entries)  # type: ignore

        return WPromise(_bind_err())
