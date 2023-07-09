from __future__ import annotations

import typing as t
from asyncio import iscoroutinefunction

import anyio

from _fp._func_types import T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, L, R, T

from .result import Err, Ok, Result


def fmap(
    fn: t.Callable[[L], t.Awaitable[T]] | t.Callable[[L], T]
) -> t.Callable[[Result[L, R]], t.Awaitable[Result[T, R]]]:
    async def _map(result: "Result[L, R]") -> "Result[T, R]":
        if result:
            if iscoroutinefunction(fn):
                return Ok(await fn(result.value))
            else:
                return Ok(fn(result.value))  # type: ignore
        return result  # type: ignore

    return _map


def fmap_err(
    fn: t.Callable[[R], t.Awaitable[T]] | t.Callable[[R], T]
) -> t.Callable[[Result[L, R]], t.Awaitable[Result[L, T]]]:
    async def _map(result: Result[L, R]) -> Result[L, T]:
        if not result:
            if iscoroutinefunction(fn):
                return Err(await fn(result.value))
            else:
                return Err(fn(result.value))  # type: ignore
        return result  # type: ignore

    return _map


def bind(
    fn: t.Callable[[L], t.Awaitable[Result[T, R]]] | t.Callable[[L], Result[T, R]]
) -> t.Callable[[Result[L, R]], t.Awaitable[Result[T, R]]]:
    async def _bind(result: Result[L, R]) -> Result[T, R]:
        if result:
            if iscoroutinefunction(fn):
                return await fn(result.value)
            else:
                return fn(result.value)  # type: ignore
        return result  # type: ignore

    return _bind


def bind_err(
    fn: t.Callable[[R], t.Awaitable[Result[L, T]]] | t.Callable[[L], Result[L, T]]
) -> t.Callable[[Result[L, R]], t.Awaitable[Result[L, T]]]:
    async def _bind(result: Result[L, R]) -> Result[L, T]:
        if not result:
            if iscoroutinefunction(fn):
                return await fn(result.value)
            else:
                return fn(result.value)  # type: ignore
        return result  # type: ignore

    return _bind


def visit(
    fn: t.Callable[[L], t.Awaitable[t.Any]] | t.Callable[[L], t.Any]
) -> t.Callable[[Result[L, R]], t.Awaitable[Result[L, R]]]:
    async def _visit(result: Result[L, R]) -> Result[L, R]:
        if result:
            if iscoroutinefunction(fn):
                await fn(result.value)
            else:
                fn(result.value)
        return result

    return _visit


def with_timeout(
    timeout: float | None,
    fn: t.Callable[[L], t.Awaitable[Result[T, R]]],
    err: t.Callable[[L], R] | t.Callable[[L], t.Awaitable[R]],
) -> t.Callable[[L], t.Awaitable[Result[T, R]]]:
    async def _with_timeout(value: L) -> Result[T, R]:
        with anyio.move_on_after(timeout):
            return await fn(value)
        if iscoroutinefunction(err):
            return Err(await err(value))  # type: ignore
        else:
            return Err(err(value))

    return _with_timeout


def within_context(
    fn: t.Callable[[L], Result[T, R]] | t.Callable[[L], t.Awaitable[Result[T, R]]],
) -> t.Callable[[t.AsyncContextManager[Result[L, R]]], t.Awaitable[Result[T, R]]]:
    if iscoroutinefunction(fn):

        async def _wrapper_async(
            context: t.AsyncContextManager[Result[L, R]]
        ) -> Result[T, R]:
            async with context as result:
                assert isinstance(result, (Ok, Err)), result
                if result:
                    return await fn(result.value)
                return result  # type: ignore

        return _wrapper_async

    async def _wrapper(context: t.AsyncContextManager[Result[L, R]]) -> Result[T, R]:
        async with context as result:
            assert isinstance(result, (Ok, Err)), result
            if result:
                return fn(result.value)  # type: ignore
            return result  # type: ignore

    return _wrapper


def bind_within_context(
    fn: t.Callable[[L], Result[T, R]] | t.Callable[[L], t.Awaitable[Result[T, R]]],
) -> t.Callable[
    [Result[t.AsyncContextManager[Result[L, R]], R]], t.Awaitable[Result[T, R]]
]:
    return bind(within_context(fn))


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], t.Awaitable[T1]] | t.Callable[[T0], T1],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T1]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], t.Awaitable[T1]] | t.Callable[[T0], T1],
    f2: t.Callable[[T1], t.Awaitable[T2]] | t.Callable[[T1], T2],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T2]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], t.Awaitable[T1]] | t.Callable[[T0], T1],
    f2: t.Callable[[T1], t.Awaitable[T2]] | t.Callable[[T1], T2],
    f3: t.Callable[[T2], t.Awaitable[T3]] | t.Callable[[T2], T3],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T3]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], t.Awaitable[T1]] | t.Callable[[T0], T1],
    f2: t.Callable[[T1], t.Awaitable[T2]] | t.Callable[[T1], T2],
    f3: t.Callable[[T2], t.Awaitable[T3]] | t.Callable[[T2], T3],
    f4: t.Callable[[T3], t.Awaitable[T4]] | t.Callable[[T3], T4],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T4]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], t.Awaitable[T1]] | t.Callable[[T0], T1],
    f2: t.Callable[[T1], t.Awaitable[T2]] | t.Callable[[T1], T2],
    f3: t.Callable[[T2], t.Awaitable[T3]] | t.Callable[[T2], T3],
    f4: t.Callable[[T3], t.Awaitable[T4]] | t.Callable[[T3], T4],
    f5: t.Callable[[T4], t.Awaitable[T5]] | t.Callable[[T4], T5],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T5]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1] | t.Callable[[T0], t.Awaitable[T1]],
    f2: t.Callable[[T1], T2] | t.Callable[[T1], t.Awaitable[T2]],
    f3: t.Callable[[T2], T3] | t.Callable[[T2], t.Awaitable[T3]],
    f4: t.Callable[[T3], T4] | t.Callable[[T3], t.Awaitable[T4]],
    f5: t.Callable[[T4], T5] | t.Callable[[T4], t.Awaitable[T5]],
    f6: t.Callable[[T5], T6] | t.Callable[[T5], t.Awaitable[T6]],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T6]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1] | t.Callable[[T0], t.Awaitable[T1]],
    f2: t.Callable[[T1], T2] | t.Callable[[T1], t.Awaitable[T2]],
    f3: t.Callable[[T2], T3] | t.Callable[[T2], t.Awaitable[T3]],
    f4: t.Callable[[T3], T4] | t.Callable[[T3], t.Awaitable[T4]],
    f5: t.Callable[[T4], T5] | t.Callable[[T4], t.Awaitable[T5]],
    f6: t.Callable[[T5], T6] | t.Callable[[T5], t.Awaitable[T6]],
    f7: t.Callable[[T6], T7] | t.Callable[[T6], t.Awaitable[T7]],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T7]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1] | t.Callable[[T0], t.Awaitable[T1]],
    f2: t.Callable[[T1], T2] | t.Callable[[T1], t.Awaitable[T2]],
    f3: t.Callable[[T2], T3] | t.Callable[[T2], t.Awaitable[T3]],
    f4: t.Callable[[T3], T4] | t.Callable[[T3], t.Awaitable[T4]],
    f5: t.Callable[[T4], T5] | t.Callable[[T4], t.Awaitable[T5]],
    f6: t.Callable[[T5], T6] | t.Callable[[T5], t.Awaitable[T6]],
    f7: t.Callable[[T6], T7] | t.Callable[[T6], t.Awaitable[T7]],
    f8: t.Callable[[T7], T8] | t.Callable[[T7], t.Awaitable[T8]],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T8]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1] | t.Callable[[T0], t.Awaitable[T1]],
    f2: t.Callable[[T1], T2] | t.Callable[[T1], t.Awaitable[T2]],
    f3: t.Callable[[T2], T3] | t.Callable[[T2], t.Awaitable[T3]],
    f4: t.Callable[[T3], T4] | t.Callable[[T3], t.Awaitable[T4]],
    f5: t.Callable[[T4], T5] | t.Callable[[T4], t.Awaitable[T5]],
    f6: t.Callable[[T5], T6] | t.Callable[[T5], t.Awaitable[T6]],
    f7: t.Callable[[T6], T7] | t.Callable[[T6], t.Awaitable[T7]],
    f8: t.Callable[[T7], T8] | t.Callable[[T7], t.Awaitable[T8]],
    f9: t.Callable[[T8], T9] | t.Callable[[T8], t.Awaitable[T9]],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T9]]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1] | t.Callable[[T0], t.Awaitable[T1]],
    f2: t.Callable[[T1], T2] | t.Callable[[T1], t.Awaitable[T2]],
    f3: t.Callable[[T2], T3] | t.Callable[[T2], t.Awaitable[T3]],
    f4: t.Callable[[T3], T4] | t.Callable[[T3], t.Awaitable[T4]],
    f5: t.Callable[[T4], T5] | t.Callable[[T4], t.Awaitable[T5]],
    f6: t.Callable[[T5], T6] | t.Callable[[T5], t.Awaitable[T6]],
    f7: t.Callable[[T6], T7] | t.Callable[[T6], t.Awaitable[T7]],
    f8: t.Callable[[T7], T8] | t.Callable[[T7], t.Awaitable[T8]],
    f9: t.Callable[[T8], T9] | t.Callable[[T8], t.Awaitable[T9]],
    f10: t.Callable[[T9], T10] | t.Callable[[T9], t.Awaitable[T10]],
    /,  # pragma: no mutate
) -> t.Callable[[T0], t.Awaitable[T10]]:
    ...


def pipe(
    __fn: t.Callable[[t.Any], t.Any] | t.Callable[[t.Any], t.Awaitable[t.Any]],
    /,
    *__fns: t.Callable[[t.Any], t.Any] | t.Callable[[t.Any], t.Awaitable[t.Any]],
) -> t.Callable[[t.Any], t.Awaitable[t.Any]]:
    """Combine several functions to create a new async function.

    Look for [point-free programming or tacit programming](https://en.wikipedia.org/wiki/Tacit_programming) to learn more about
    the pattern and its usages.

    Name is borrowed from Linux, which uses this paradigm with pipes.
    """

    async def _pipe(x: t.Any) -> t.Any:
        if iscoroutinefunction(__fn):
            result = await __fn(x)
        else:
            result = __fn(x)
        for fn in __fns:
            if iscoroutinefunction(fn):
                result = await fn(result)
            else:
                result = fn(result)
        return result

    return _pipe
