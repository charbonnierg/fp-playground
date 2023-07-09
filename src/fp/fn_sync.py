from __future__ import annotations

import typing as t
from asyncio import iscoroutinefunction

from _fp._func_types import T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, L, R, T

from .result import Err, Ok, Result


def fmap(fn: t.Callable[[L], T]) -> t.Callable[[Result[L, R]], Result[T, R]]:
    """Create a function that applies a function to the value contained in `Ok` result,
    or forwards `Err` result."""

    def _map(result: Result[L, R]) -> Result[T, R]:
        if result:
            return Ok(fn(result.value))
        return result  # type: ignore

    return _map


def fmap_err(fn: t.Callable[[R], T]) -> t.Callable[[Result[L, R]], Result[L, T]]:
    """Create a function that applies a function to the value contained in `Err` result,
    or forwards `Ok` result."""

    def _map(result: Result[L, R]) -> Result[L, T]:
        if not result:
            return Err(fn(result.value))
        return result  # type: ignore

    return _map


def bind(fn: t.Callable[[L], Result[T, R]]) -> t.Callable[[Result[L, R]], Result[T, R]]:
    """Create a function that applies a function which must return a result to the value
    contained in `Ok` result, or forwards `Err` result."""

    def _bind(result: Result[L, R]) -> Result[T, R]:
        if result:
            return fn(result.value)
        return result  # type: ignore

    return _bind


def bind_err(
    fn: t.Callable[[R], Result[L, T]]
) -> t.Callable[[Result[L, R]], Result[L, T]]:
    """Create a function that applies a function which must return a result to the value
    contained in `Err` result, or forwards `Ok` result."""

    def _bind(result: Result[L, R]) -> Result[L, T]:
        if not result:
            return fn(result.value)
        return result  # type: ignore

    return _bind


def visit(fn: t.Callable[[L], t.Any]) -> t.Callable[[Result[L, R]], Result[L, R]]:
    """Create a function that execute a function using the value contained in `Ok` result,
    or forwards `Err` result. In both cases, the result is returned unchanged (identity).
    """

    def _visit(result: Result[L, R]) -> Result[L, R]:
        if result:
            fn(result.value)
        return result

    return _visit


@t.overload  # pragma: no mutate
def within_context(
    func: t.Callable[[L], t.Awaitable[Result[T, R]]],
) -> t.Callable[[t.ContextManager[Result[L, R]]], t.Awaitable[Result[T, R]]]:
    ...


@t.overload  # pragma: no mutate
def within_context(
    func: t.Callable[[L], Result[T, R]],
) -> t.Callable[[t.ContextManager[Result[L, R]]], Result[T, R]]:
    ...


def within_context(
    func: t.Callable[[t.Any], t.Any],
) -> t.Callable[[t.Any], t.Any]:
    """Create a function that applies a function to the value contained in `Ok` result,
    returned by an async context manager or forwards `Err` result."""
    if iscoroutinefunction(func):

        async def _wrapper_async(context: t.ContextManager[t.Any]) -> t.Any:
            with context as result:
                if result:
                    return await func(result.value)
                return result

        return _wrapper_async

    def _wrapper(context: t.ContextManager[t.Any]) -> t.Any:
        with context as result:
            if result:
                return func(result.value)
            return result

    return _wrapper


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T1]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T2]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T3]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    f4: t.Callable[[T3], T4],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T4]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    f4: t.Callable[[T3], T4],
    f5: t.Callable[[T4], T5],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T5]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    f4: t.Callable[[T3], T4],
    f5: t.Callable[[T4], T5],
    f6: t.Callable[[T5], T6],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T6]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    f4: t.Callable[[T3], T4],
    f5: t.Callable[[T4], T5],
    f6: t.Callable[[T5], T6],
    f7: t.Callable[[T6], T7],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T7]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    f4: t.Callable[[T3], T4],
    f5: t.Callable[[T4], T5],
    f6: t.Callable[[T5], T6],
    f7: t.Callable[[T6], T7],
    f8: t.Callable[[T7], T8],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T8]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    f4: t.Callable[[T3], T4],
    f5: t.Callable[[T4], T5],
    f6: t.Callable[[T5], T6],
    f7: t.Callable[[T6], T7],
    f8: t.Callable[[T7], T8],
    f9: t.Callable[[T8], T9],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T9]:
    ...


@t.overload  # pragma: no mutate
def pipe(
    f1: t.Callable[[T0], T1],
    f2: t.Callable[[T1], T2],
    f3: t.Callable[[T2], T3],
    f4: t.Callable[[T3], T4],
    f5: t.Callable[[T4], T5],
    f6: t.Callable[[T5], T6],
    f7: t.Callable[[T6], T7],
    f8: t.Callable[[T7], T8],
    f9: t.Callable[[T8], T9],
    f10: t.Callable[[T9], T10],
    /,  # pragma: no mutate
) -> t.Callable[[T0], T10]:
    ...


def pipe(
    __fn: t.Callable[[t.Any], t.Any],
    /,
    *__fns: t.Callable[[t.Any], t.Any],
) -> t.Any:
    """Combine several functions to create a new function.

    Look for [point-free programming or tacit programming](https://en.wikipedia.org/wiki/Tacit_programming) to learn more about
    the pattern and its usages.

    Name is borrowed from Linux, which uses this paradigm with pipes.
    """

    def _pipe(x: t.Any) -> t.Any:
        result = __fn(x)
        for fn in __fns:
            result = fn(result)
        return result

    return _pipe
