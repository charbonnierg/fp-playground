from __future__ import annotations

import abc
import typing as t
from dataclasses import dataclass
from enum import IntEnum

from typing_extensions import Never, Self, reveal_type

from fp import Result, bind_err, pipe
from fp.result import Err
from fp.struct.error import Error


def assert_never(x: Never) -> Never:  # type: ignore
    pass


class CodeInContext1(IntEnum):
    FAIL_TO_DO_SOMETHING = 1
    DISCONNECTED_FROM_SOMEWHERE = 2
    BAD_PASSWORD = 3
    BAD_PRIVATE_KEY = 4


class ErrorInContext1(Error[CodeInContext1, str]):
    @classmethod
    def create(cls, code: CodeInContext1, msg: str = "") -> ErrorInContext1:
        return cls(code=code, detail=msg)


T = t.TypeVar("T")
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

    def convert_error_from_context_1(
        self, error: ErrorInContext1
    ) -> Err[t.Any, DomainError]:
        if (
            error.code == CodeInContext1.BAD_PASSWORD
            or error.code == CodeInContext1.BAD_PRIVATE_KEY
        ):
            return DomainError.err(DomainCode.NOT_ALLOWED, "Bad credentials")
        if (
            error.code == CodeInContext1.DISCONNECTED_FROM_SOMEWHERE
            or error.code == CodeInContext1.FAIL_TO_DO_SOMETHING
        ):
            return DomainError.err(DomainCode.RETRY_LATER, "Please try again later")
        assert_never(error.code)
        return DomainError.err(DomainCode.INTERNAL_ERROR)

    def convert_error_from_context_2(
        self, error: ErrorInContext2
    ) -> Err[t.Any, DomainError]:
        if error.code == CodeInContext2.DISCONNECTED_FROM_SOMEWHERE_ELSE:
            return DomainError.err(DomainCode.RETRY_LATER, "Please try again later")
        if error.code == CodeInContext2.FAIL_TO_DO_SOMETHING_ELSE:
            return DomainError.err(DomainCode.INTERNAL_ERROR)
        assert_never(error.code)
        return DomainError.err(DomainCode.INTERNAL_ERROR)

    def do_action(self):
        return (
            self.adapter_1.do_something()
            .bind_err(self.convert_error_from_context_1)
            .bind(
                pipe(
                    self.adapter_2.do_something_else,
                    bind_err(self.convert_error_from_context_2),
                )
            )
        )


@dataclass
class Usecase:
    service: DomainService

    def execute(self):
        return self.service.do_action()


def main(adapter1: Context1Adapter, adapter2: Context2Adapter):
    service = DomainService(adapter1, adapter2)
    result = Usecase(service).execute()
    reveal_type(result)
