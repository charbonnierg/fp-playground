from typing import Literal

from fp.promise import Err, Ok, Result


async def coro_returns_ok():
    return Ok(1)


async def coro_returns_value():
    return 1


async def plus_one_async(value: int):
    return value + 1


async def plus_one_async_ok(value: int):
    return Ok(value + 1)


async def plus_one_async_err(value: int):
    return Err(value + 1)


def fail_if_called(value: object):
    raise AssertionError


async def async_fail_if_called(value: object):
    raise AssertionError


class Context:
    def __init__(self, fail_on: None | Literal["enter", "get"]):
        self.fail_on = fail_on

    def __enter__(self):
        if self.fail_on == "enter":
            return Err("fail on enter")
        return Ok(self)

    async def __aenter__(self):
        return self.__enter__()

    def __exit__(self, *args: object, **kwds: object) -> None:
        pass

    async def __aexit__(self, *args: object, **kwds: object) -> None:
        pass

    def get_something(self):
        if self.fail_on == "get":
            return Err("fail on get")
        return Ok(1)

    async def get_something_async(self):
        return self.get_something()

    @classmethod
    def create(
        cls, fail_on: None | Literal["create", "enter", "get"]
    ) -> "Result[Context, str]":
        if fail_on == "create":
            return Err("fail on create")
        return Ok(cls(fail_on))
