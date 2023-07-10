from __future__ import annotations

import abc
import typing as t
from dataclasses import dataclass
from enum import IntEnum

from typing_extensions import Self, reveal_type

from fp import Result
from fp.result import Err
from fp.struct.error import Error

T = t.TypeVar("T")


class CodeInContext1(IntEnum):
    FAIL_TO_DO_SOMETHING = 1
    DISCONNECTED_FROM_SOMEWHERE = 2
    BAD_PASSWORD = 3
    BAD_PRIVATE_KEY = 4


class ErrorInContext1(Error[CodeInContext1, str]):
    @classmethod
    def create(cls, code: CodeInContext1, msg: str = "") -> ErrorInContext1:
        return cls(code=code, detail=msg)


ResultInContext1 = Result[T, ErrorInContext1]


class Context1Adapter(metaclass=abc.ABCMeta):
    def do_something(self) -> ResultInContext1[str]:
        raise NotImplementedError


class CodeInContext2(IntEnum):
    FAIL_TO_DO_SOMETHING_ELSE = 1
    DISCONNECTED_FROM_SOMEWHERE_ELSE = 2


class ErrorInContext2(Error[CodeInContext2, str]):
    @classmethod
    def create(cls, code: CodeInContext2, msg: str = "") -> ErrorInContext2:
        return cls(code=code, detail=msg)


ResultInContext2 = Result[T, ErrorInContext2]


class Context2Adapter(metaclass=abc.ABCMeta):
    def do_something_else(self, input_value: str) -> ResultInContext2[int]:
        raise NotImplementedError


class DomainCode(IntEnum):
    RETRY_LATER = 0
    NOT_ENOUGH_MONEY = 1
    NOT_OLD_ENOUGH = 2
    NOT_ALLOWED = 3
    INTERNAL_ERROR = 4


class DomainError(Error[DomainCode, str]):
    @classmethod
    def err(cls: type[Self], code: DomainCode, msg: str = "") -> Err[t.Any, Self]:
        return Err(cls(code=code, detail=msg))


def some_condition(value: int) -> bool:
    return value > 18


@dataclass
class DomainService:
    adapter_1: Context1Adapter
    adapter_2: Context2Adapter

    def do_action(self):
        result = self.adapter_1.do_something()
        if not result:
            return result

        result = self.adapter_2.do_something_else(result.value)
        if not result:
            return result

        if not some_condition(result.value):
            return DomainError.err(DomainCode.NOT_OLD_ENOUGH)

        return t.cast(Result[int, DomainError], result)


@dataclass
class Usecase:
    service: DomainService

    def execute(self):
        result = self.service.do_action()
        if not result:
            return result

        return result


def main(adapter1: Context1Adapter, adapter2: Context2Adapter):
    service = DomainService(adapter1, adapter2)
    result = Usecase(service).execute()
    reveal_type(result)
