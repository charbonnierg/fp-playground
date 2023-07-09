from __future__ import annotations

import typing as t
from asyncio import iscoroutinefunction

from ._result_types import L, R, T
from .result import Err, Ok, Result


class Promise(t.Generic[L, R]):
    """A promise of a Result which will be returned by a coroutine function or an awaitable.

    A Promise is a generic type of `L` and `R`, where `Result[L, R]` is the result type
    of the coroutine function or the awaitable it wraps.
    """

    _coro: t.Awaitable[Result[L, R]]

    def __init__(self, coro: t.Awaitable[Result[L, R]]):
        self._coro = coro

    def __await__(self) -> t.Generator[t.Any, None, Result[L, R]]:
        """Await the coroutine wrapped by the promise and return a result."""
        return self._coro.__await__()

    @classmethod
    def of_ok(cls, coro: t.Awaitable[L]) -> Promise[L, R]:
        """Create a promise of an `Ok` value from a coroutine function or an awaitable."""

        async def _of_ok() -> Result[L, R]:
            return Ok(await coro)

        return Promise(_of_ok())

    @classmethod
    def of_err(cls, coro: t.Awaitable[R]) -> Promise[L, R]:
        """Create a promise of an `Err` value from a coroutine function or an awaitable."""

        async def _of_ok() -> Result[L, R]:
            return Err(await coro)

        return Promise(_of_ok())

    def map(
        self,
        fn: t.Callable[[L], T] | t.Callable[[L], t.Awaitable[T]],
    ) -> Promise[T, R]:
        """Apply a function to the value contained in `Ok` promise result,
        or forward `Err` promise result."""

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
