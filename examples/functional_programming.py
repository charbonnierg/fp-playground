from __future__ import annotations

import asyncio
from typing import Any, AsyncContextManager

from fp import Err, Ok, Promise, Result, aio, bind, bind_err, fmap, fmap_err


class ConnectOptions:
    def __init__(
        self,
        fail_on_creation: bool = False,
        fail_on_connection: bool = False,
        fail_on_fetch: bool = False,
    ) -> None:
        self.fail_on_creation = fail_on_creation
        self.fail_on_connection = fail_on_connection
        self.fail_on_fetch = fail_on_fetch


async def create_connection(
    options: ConnectOptions | None = None,
) -> Result[Connection, str]:
    if options and options.fail_on_creation:
        return Err("Failed to create connection")
    return Ok(Connection(options))


class Connection(AsyncContextManager["Result[Connection, str]"]):
    def __init__(self, options: ConnectOptions | None = None):
        self.options = options or ConnectOptions()

    async def __aenter__(self) -> Result[Connection, str]:
        print("Opening connection")
        if self.options.fail_on_connection:
            return Err("Failed to connect")
        return Ok(self)

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        print("Closing connection")

    async def get_value(self) -> Result[int, str]:
        if self.options.fail_on_fetch:
            return Err("Failed to get value")
        return Ok(1)


def divide(x: int) -> Result[float, str]:
    try:
        return Ok(1 / x)
    except ZeroDivisionError:
        return Err("BOOM")


f = aio.pipe(
    # Returns a context manager
    create_connection,
    # Execute a function (possibly async) within the context manager which must return a Result
    aio.bind_within_context(Connection.get_value),
    # Execute a function using the result of the previous function (executed within context)
    bind(divide),
    # Transform Ok value
    fmap(lambda value: value**2),
    # Transform Err value
    fmap_err(str.upper),
    # Transform Ok value into a new Result
    bind(lambda value: Ok(value)),
    # Transform Err value into a new Result
    bind_err(lambda msg: Err(msg)),
)


async def second_example(options: ConnectOptions | None = None) -> Result[float, str]:
    # Second example: Using methods
    # Does not use intermediate function
    # Start by creating a promise which returns result of context manager
    # Execute a function (possibly async) within the context manager
    # Execute a function using the result of the previous function (executed within context)
    # Transform Ok value
    # Transform Err value
    # Transform Ok value into a new Result
    # Transform Err value into a new Result
    return await (
        Promise(create_connection(options))
        .bind(aio.within_context(Connection.get_value))
        .bind(divide)
        .map(lambda value: value**2)
        .map_err(lambda msg: msg.upper())
        .bind(lambda value: Ok(value + 2))
        .bind_err(lambda msg: Err(msg))
    )


# Third example: if/else branching
def third_example(result: Result[int, str]) -> None:
    if result:
        print(result)
    else:
        print(result)


assert asyncio.run(second_example(None)) == Ok(3.0)
